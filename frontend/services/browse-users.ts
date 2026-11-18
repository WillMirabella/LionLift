import type { BrowseOptions } from './browse-options';

// Only the public fields needed by Browse, not the full account model.
export type BrowseUser = {
  id: number;
  first_name: string | null;
  last_name: string | null;
  major: string | null;
  grad_year: number | null;
  car_id: number | null;
};

export function buildBrowseUrl(baseUrl: string, options: BrowseOptions) {
  const query = new URLSearchParams();
  if (options.sort) query.set('sort', options.sort);
  if (options.role) query.set('role', options.role);
  if (options.graduationYear) query.set('grad_year', options.graduationYear);
  return `${baseUrl.replace(/\/+$/, '')}/api/users/${query.size ? `?${query}` : ''}`;
}

export async function fetchBrowseUsers(options: BrowseOptions, signal?: AbortSignal): Promise<BrowseUser[]> {
  const baseUrl = process.env.EXPO_PUBLIC_API_URL;
  if (!baseUrl) throw new Error('The server address is not configured.');
  const response = await fetch(buildBrowseUrl(baseUrl, options), { signal });
  if (!response.ok) throw new Error(`Could not load users (server error ${response.status}).`);
  const users: unknown = await response.json();
  if (!Array.isArray(users) || !users.every(user =>
    user && typeof user.id === 'number' &&
    (user.first_name === null || typeof user.first_name === 'string') &&
    (user.last_name === null || typeof user.last_name === 'string') &&
    (user.major === null || typeof user.major === 'string') &&
    (user.grad_year === null || typeof user.grad_year === 'number') &&
    (user.car_id === null || typeof user.car_id === 'number')
  )) throw new Error('The server returned an unexpected user list.');
  return users;
}
