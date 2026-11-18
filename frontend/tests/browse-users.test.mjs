import { test } from 'node:test';
import assert from 'node:assert/strict';
import { buildBrowseUrl, fetchBrowseUsers } from '../services/browse-users.ts';

const defaults = { sort: '', role: '', graduationYear: '' };

test('builds API parameters and clears them for Reset', () => {
  const url = new URL(buildBrowseUrl('http://localhost:5000/', {
    sort: '-grad_year', role: 'driver', graduationYear: '2027',
  }));
  assert.equal(url.pathname, '/api/users/');
  assert.equal(url.searchParams.get('sort'), '-grad_year');
  assert.equal(url.searchParams.get('role'), 'driver');
  assert.equal(url.searchParams.get('grad_year'), '2027');
  assert.equal(buildBrowseUrl('http://localhost:5000/', defaults), 'http://localhost:5000/api/users/');
});

test('handles results, empty lists, failures, and cancellation', async t => {
  const originalUrl = process.env.EXPO_PUBLIC_API_URL;
  t.after(() => {
    if (originalUrl === undefined) delete process.env.EXPO_PUBLIC_API_URL;
    else process.env.EXPO_PUBLIC_API_URL = originalUrl;
  });
  process.env.EXPO_PUBLIC_API_URL = 'http://localhost:5000';
  const users = [{ id: 2, first_name: 'Alex', last_name: null, major: null, grad_year: 2027, car_id: 1 }];
  const fetchMock = t.mock.method(globalThis, 'fetch', async () => Response.json(users));
  assert.deepEqual(await fetchBrowseUsers(defaults), users);
  fetchMock.mock.mockImplementation(async () => Response.json([]));
  assert.deepEqual(await fetchBrowseUsers(defaults), []);
  fetchMock.mock.mockImplementation(async () => new Response('', { status: 500 }));
  await assert.rejects(fetchBrowseUsers(defaults), /server error 500/);
  fetchMock.mock.mockImplementation(async () => Response.json({ users }));
  await assert.rejects(fetchBrowseUsers(defaults), /unexpected user list/);
  fetchMock.mock.mockImplementation(async () => { throw new TypeError('Network unavailable'); });
  await assert.rejects(fetchBrowseUsers(defaults), /Network unavailable/);
  const controller = new AbortController();
  controller.abort();
  fetchMock.mock.mockImplementation(async (_url, { signal }) => {
    assert.equal(signal, controller.signal);
    signal.throwIfAborted();
  });
  await assert.rejects(fetchBrowseUsers(defaults, controller.signal), { name: 'AbortError' });
  delete process.env.EXPO_PUBLIC_API_URL;
  await assert.rejects(fetchBrowseUsers(defaults), /not configured/);
});
