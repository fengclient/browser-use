from browser_use.browser.watchdogs.local_browser_watchdog import LocalBrowserWatchdog


def test_local_browser_watchdog_reuses_configured_remote_debugging_port():
	launch_args = [
		'--user-data-dir=/tmp/browser-use',
		'--remote-debugging-port=9222',
	]

	port = LocalBrowserWatchdog._get_configured_remote_debugging_port(launch_args)

	assert port == 9222


def test_local_browser_watchdog_ignores_missing_remote_debugging_port():
	launch_args = ['--user-data-dir=/tmp/browser-use']

	port = LocalBrowserWatchdog._get_configured_remote_debugging_port(launch_args)

	assert port is None


def test_local_browser_watchdog_prefers_last_remote_debugging_port():
	launch_args = [
		'--remote-debugging-port=9222',
		'--remote-debugging-port=9333',
	]

	port = LocalBrowserWatchdog._get_configured_remote_debugging_port(launch_args)

	assert port == 9333
