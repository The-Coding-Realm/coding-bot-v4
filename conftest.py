def pytest_addoption(parser):
    parser.addoption("--token", action="store")


def pytest_generate_tests(metafunc):
    # This is called for every test. Only get/set command line arguments
    # if the argument is specified in the list of test "fixturenames".
    if 'token' in metafunc.fixturenames:
        metafunc.parametrize("token", metafunc.config.getoption('token'))
