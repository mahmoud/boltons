def test_flatapi():
    import boltons
    # calling enable flatapi will make everything top level
    boltons.enable_flatapi()
    assert hasattr(boltons, 'get_python_info')
    boltons.get_python_info()
