This directory will contain our frontend mobile application.
We will be using Expo for development of React Native.

### Setup on your machine

- Move into the frontend directory
  - cd frontend
- Install dependencies
  - npm install

### Running the app

- Start the server (from the frontend directory)
  - npx expo start
- Scan the QR code with your phone or choose an option on your computer

### Navigation

`frontend/index.ts` starts Expo Router; it is the entry point configured in
`package.json`. `app/index.tsx` is a different file: it redirects the root
route `/` to `/find-drivers` and is hidden from the tab bar.

`app/_layout.tsx` defines `NavBar`, with **Find Drivers**, **Map**, and **Profile**
tabs. Each tab's title is also its screen header. Each route file contains its
screen component directly:

- `app/find-drivers.tsx` defines `FindDriversScreen`.
- `app/map.tsx` defines `MapScreen`.
- `app/profile.tsx` defines `ProfileScreen`.

The screens share `components/placeholder-screen.tsx` and
`constants/screen-styles.ts`. Update those files to change all placeholder cards.
Build each feature in its route file and keep reusable components in
`components/`, which also contains `user-card.tsx`. Driver search, the interactive
map, and profile editing are future work.

The tab bar's height includes the device's bottom safe area so controls stay
above the home indicator. It does not add a separate minimum-height gap.
The unused `App.tsx` starter has been removed.

Keep `package-lock.json` committed alongside dependency changes. It records exact
versions for consistent installs across teammates and supports `npm ci`.

### User view selector (issue #24)

Find Drivers has one Display options icon on the right of its screen header.
It opens a menu with a View section containing Compact and Expanded choices.
The selected choice has a checkmark and light blue background. Selecting a view
closes the menu and updates every card together. The menu can also be dismissed
with its close button, by tapping outside it, or with Android Back / web Escape.
Sorting and filtering can be added as sections of the same menu in future work;
no nonfunctional sorting or filtering controls are displayed.

Compact is selected initially. The screen holds one `expanded` state and passes
it to `components/user-view-selector.tsx` and every `UserCard`. The selector
handles its own menu visibility and reports selections through `onChange`.
Controls have accessibility labels and at least 44-pixel touch targets.

Expanded shows the card's existing map placeholder; Compact hides it. The cards
still display sample information, and the map is not interactive.

To check this feature, open Find Drivers and confirm both cards start compact.
Open Display options from the header and select Expanded. Confirm the menu
closes and both map placeholders appear. Reopen the menu and confirm Expanded
is selected, then select Compact and confirm both placeholders disappear.
Check that dismissing the menu without selecting a view preserves the layout.
Switch to another tab and back, and confirm the control belongs only to Find Drivers.

### Verify changes

- Install dependencies with `npm ci` (Node.js 22.13 or newer).
- Run `npm run lint` and `npm run typecheck`.
- Run `npx expo start`, then open the app in Expo Go.
- Confirm Find Drivers appears first. Tap Map, Profile, and Find Drivers and
  confirm the screen title and selected tab change together.
- Check that only three tabs appear, the header matches the selected screen, and
  the tab bar reaches the bottom safe area without an extra blank strip.
- Open `/`, `/find-drivers`, `/map`, and `/profile` in the browser to check routes.
- For browser preview, run `npm run web`.
