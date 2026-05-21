"""
Export full browser storage state including localStorage and sessionStorage

The default export_storage_state() only exports cookies (origins is empty).
This example shows how to also capture localStorage/sessionStorage via
the internal _cdp_get_storage_state() method.

Caveats:
  - Origin discovery relies on Page.getFrameTree(), so only origins from
    currently loaded frames are captured. If you need storage from a domain
    that isn't present in the page's frame tree, navigate there first.
  - localStorage can be large (up to 5-10MB per origin). The exported file
    may be significantly bigger than a cookies-only export.
  - sessionStorage is tied to a tab session; restoring it into a new tab
    is best-effort and may not preserve the exact browser semantics.
  - localStorage values are JS-accessible and may contain sensitive tokens
    (JWT, OAuth state, etc.). Handle the exported file with care.
"""

import asyncio
import json
import os
import sys
from pathlib import Path

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from dotenv import load_dotenv

load_dotenv()

from browser_use import Browser


def select_chrome_profile() -> str | None:
	"""Prompt user to select a Chrome profile."""
	profiles = Browser.list_chrome_profiles()
	if not profiles:
		return None

	print('Available Chrome profiles:')
	for i, p in enumerate(profiles, 1):
		print(f'  {i}. {p["name"]}')

	while True:
		choice = input(f'\nSelect profile (1-{len(profiles)}): ').strip()
		if choice.isdigit() and 1 <= int(choice) <= len(profiles):
			return profiles[int(choice) - 1]['directory']
		print('Invalid choice, try again.')


async def export_full_storage_state(browser: Browser, output_path: str | Path, origin_filter: set[str] | None = None) -> dict:
	"""Export cookies + localStorage + sessionStorage in Playwright storage_state format.

	Args:
		browser: Running Browser instance.
		output_path: Path to save the JSON file.
		origin_filter: If set, only export storage for these origins (e.g. {'https://app.example.com'}).
			If None, export all discovered origins.
	"""
	raw_state = await browser._cdp_get_storage_state()

	origins = raw_state.get('origins', [])
	if origin_filter is not None:
		origins = [o for o in origins if o['origin'] in origin_filter]

	storage_state = {
		'cookies': [
			{
				'name': c['name'],
				'value': c['value'],
				'domain': c['domain'],
				'path': c['path'],
				'expires': c.get('expires', -1),
				'httpOnly': c.get('httpOnly', False),
				'secure': c.get('secure', False),
				'sameSite': c.get('sameSite', 'Lax'),
			}
			for c in raw_state.get('cookies', [])
		],
		'origins': origins,
	}

	output_file = Path(output_path).expanduser().resolve()
	output_file.parent.mkdir(parents=True, exist_ok=True)
	output_file.write_text(json.dumps(storage_state, indent=2, ensure_ascii=False), encoding='utf-8')

	cookie_count = len(storage_state['cookies'])
	origin_count = len(origins)
	print(f'Exported {cookie_count} cookies and {origin_count} origins to {output_file}')
	return storage_state


async def main():
	profile = select_chrome_profile()
	if not profile:
		print('No Chrome profiles found.')
		return

	browser = Browser.from_system_chrome(profile_directory=profile)

	await browser.start()

	# Option 1: Export cookies only (default behavior)
	await browser.export_storage_state('cookies_only.json')

	# Option 2: Export full storage (cookies + localStorage + sessionStorage)
	await export_full_storage_state(browser, 'full_storage_state.json')

	# Option 3: Export full storage but only for specific origins
	# Useful when you only need auth-related storage and want to avoid
	# dumping large caches or sensitive data from unrelated domains
	# await export_full_storage_state(
	# 	browser,
	# 	'filtered_storage_state.json',
	# 	origin_filter={'https://app.example.com', 'https://auth.example.com'},
	# )

	await browser.stop()


if __name__ == '__main__':
	asyncio.run(main())
