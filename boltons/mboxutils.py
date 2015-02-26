# -*- coding: utf-8 -*-
"""\
Useful utilities for working with mailboxes. Credit to Mark
Williams for these.
"""

import mailbox
import tempfile


class mbox_readonlydir(mailbox.mbox):
    """\
    A subclass of mbox suitable for use with mboxs insides a read-only
    /var/mail directory.

    Deletes messages via truncation, in the manner of heirloom-mailx.

    The `maxmem` specifies the largest sized mailbox to attempt to
    copy into RAM.  Larger mailboxes will be copied incrementally
    which is more hazardous.

    NB: This can corrupt your mailbox!  Only use this if you know you
    need it.
    """

    def __init__(self, path, factory=None, create=True, maxmem=1024 * 1024):
        mailbox.mbox.__init__(self, path, factory, create)
        self.maxmem = maxmem

    def flush(self):
        """\
        Write any pending changes to disk.

        NB: This deletes messages via truncation, so if it fails
        halfway through it may corrupt your mailbox!  Use only if you
        must.
        """

        # Appending and basic assertions are the same as in mailbox.mbox.flush.
        if not self._pending:
            if self._pending_sync:
                # Messages have only been added, so syncing the file
                # is enough.
                mailbox._sync_flush(self._file)
                self._pending_sync = False
            return

        # In order to be writing anything out at all, self._toc must
        # already have been generated (and presumably has been modified
        # by adding or deleting an item).
        assert self._toc is not None

        # Check length of self._file; if it's changed, some other process
        # has modified the mailbox since we scanned it.
        self._file.seek(0, 2)
        cur_len = self._file.tell()
        if cur_len != self._file_length:
            raise mailbox.ExternalClashError('Size of mailbox file changed '
                                             '(expected %i, found %i)' %
                                             (self._file_length, cur_len))

        self._file.seek(0)

        # Truncation logic begins here.  Mostly the same except we
        # can use tempfile because we're not doing rename(2).
        with tempfile.TemporaryFile() as new_file:
            new_toc = {}
            self._pre_mailbox_hook(new_file)
            for key in sorted(self._toc.keys()):
                start, stop = self._toc[key]
                self._file.seek(start)
                self._pre_message_hook(new_file)
                new_start = new_file.tell()
                while True:
                    buffer = self._file.read(min(4096,
                                                 stop - self._file.tell()))
                    if buffer == '':
                        break
                    new_file.write(buffer)
                new_toc[key] = (new_start, new_file.tell())
                self._post_message_hook(new_file)
            self._file_length = new_file.tell()

            self._file.seek(0)
            new_file.seek(0)

            # Copy back our messages
            if self._file_length <= self.maxmem:
                self._file.write(new_file.read())
            else:
                while True:
                    buffer = new_file.read(4096)
                    if not buffer:
                        break
                    self._file.write(buffer)

            # Delete the rest.
            self._file.truncate()

        # Same wrap up.
        self._toc = new_toc
        self._pending = False
        self._pending_sync = False
        if self._locked:
            mailbox._lock_file(self._file, dotlock=False)
