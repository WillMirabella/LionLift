export type BrowseOptions = {
  sort: '' | 'first_name' | '-first_name' | 'grad_year' | '-grad_year';
  role: '' | 'driver' | 'rider';
  graduationYear: string;
};

export const defaultBrowseOptions: BrowseOptions = {
  sort: '', role: '', graduationYear: '',
};

