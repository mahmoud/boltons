import mailbox
from contextlib import closing

import pytest

from boltons.mboxutils import mbox_readonlydir


class _CappedReadFile:
    def __init__(self, stream):
        self.stream = stream
        self.reads = 0

    def read(self, size=-1):
        self.reads += 1
        if self.reads > 100:
            raise RuntimeError('message copy did not terminate at EOF')
        return self.stream.read(size)

    def __getattr__(self, name):
        return getattr(self.stream, name)


@pytest.mark.parametrize('maxmem', [0, 1024 * 1024])
def test_mbox_readonlydir_flush_after_removal(tmp_path, maxmem):
    path = str(tmp_path / 'messages.mbox')
    messages = [b'Subject: first\n\nfirst body\n',
                b'Subject: removed\n\nremoved body\n',
                b'Subject: last\n\nlast body\n']
    with closing(mailbox.mbox(path)) as original:
        keys = [original.add(message) for message in messages]

    box = mbox_readonlydir(path, maxmem=maxmem)
    box._file = _CappedReadFile(box._file)
    try:
        del box[keys[1]]
        box.flush()
        assert [message['Subject'] for message in box] == ['first', 'last']
        assert [message.get_payload() for message in box] == ['first body\n', 'last body\n']
        box.flush()  # no pending changes
    finally:
        # Avoid retrying a failing flush during cleanup on the old code.
        box._pending = False
        box.close()

    with closing(mailbox.mbox(path, create=False)) as reopened:
        assert [message['Subject'] for message in reopened] == ['first', 'last']
        assert [message.get_payload() for message in reopened] == ['first body\n', 'last body\n']
