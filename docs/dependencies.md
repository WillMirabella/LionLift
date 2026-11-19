# Project Dependencies

This document lists the packages declared in the LionLift backend and frontend,
explains their purpose, and records the results of a source-code usage review.

Versions are taken from `backend/requirements.txt` and
`frontend/package.json`. Frontend version prefixes (`^` and `~`) are preserved
as declared.

## Backend Dependencies

Source: `backend/requirements.txt`

| Package | Version | Purpose |
|---|---|---|
| Flask | `3.1.3` | Python web framework used to create the LionLift backend application, register routes, handle HTTP requests, and return API responses. |
| psycopg2 | `2.9.13` | PostgreSQL database adapter for Python. Used by the backend database module to connect to PostgreSQL and execute database operations. |

Both backend dependencies are directly imported in the backend source code.

## Frontend Dependencies

Source: `frontend/package.json`, under `dependencies`.

| Package | Version | Purpose |
|---|---|---|
| `@expo/vector-icons` | `^15.1.1` | Provides icon sets used by the React Native interface, including Ionicons. |
| `expo` | `^58.0.21` | Expo framework and development tools used to run and build the application. Also provides the base TypeScript configuration. |
| `expo-constants` | `~58.0.14` | Provides access to app configuration and runtime constants. |
| `expo-font` | `~58.0.11` | Supports loading fonts in the Expo application and is registered as an Expo config plugin. |
| `expo-linking` | `~58.0.15` | Provides utilities for handling deep links and application URLs. |
| `expo-router` | `~58.0.28` | Provides file-based navigation and routing between application screens. |
| `expo-status-bar` | `~58.0.4` | Provides control over the device status bar appearance. |
| `react` | `19.3.1` | JavaScript library used to build the application's component-based user interface and manage component state. |
| `react-dom` | `19.3.1` | Provides React rendering support for web platforms. |
| `react-native` | `0.88.1` | Framework for building the application's native mobile interface using React components. |
| `react-native-otp-entry` | `1.8.6` | Provides an input component for entering one-time verification codes. |
| `react-native-reanimated` | `4.7.1` | Provides animation APIs for React Native interfaces. |
| `react-native-safe-area-context` | `~5.11.0` | Handles safe screen areas so interface elements avoid notches, system bars, and other screen insets. |
| `react-native-screens` | `~4.30.1` | Provides native screen containers and navigation-related screen optimizations. |
| `react-native-web` | `^0.21.4` | Allows React Native components to render in web browsers. |
| `react-native-worklets` | `0.13.1` | Provides worklet functionality used by animation and related runtime libraries. |

## Frontend Development Dependencies

Source: `frontend/package.json`, under `devDependencies`.

| Package | Version | Purpose |
|---|---|---|
| `@types/react` | `~19.3.0` | Provides TypeScript type definitions for React. |
| `eslint` | `^10.13.0` | JavaScript and TypeScript linting tool used to identify code-quality and potential programming issues. |
| `eslint-config-expo` | `~58.0.4` | Provides Expo-specific ESLint rules and configuration for the frontend project. |
| `typescript` | `~7.0.2` | Provides static type checking and TypeScript compilation tools. |

## Dependency Usage Review

The source code was searched for Python imports, JavaScript and TypeScript imports, and CommonJS `require()` statements. Frontend configuration files and package scripts were also inspected.

### Backend

Both declared backend packages are directly imported:

- `Flask` is imported by `backend/app.py` and the route modules.
- `psycopg2` is imported by `backend/db.py`.

No unused backend dependencies were identified.

### Frontend

The following packages have direct imports in the application source:

- `@expo/vector-icons`
- `expo-router`
- `react`
- `react-native`
- `react-native-otp-entry`
- `react-native-safe-area-context`

Other packages have identifiable configuration, tooling, or framework roles:

- `expo` is used by the frontend scripts and the TypeScript configuration.
- `expo-font` is registered in `app.json`.
- `eslint-config-expo` is imported in `eslint.config.js`.
- `eslint` is used by the lint script.
- `typescript` is used by the typecheck script.

### Packages Not Directly Imported

The following packages did not appear in the searched application imports or inspected configuration references:

- `expo-constants`
- `expo-linking`
- `expo-status-bar`
- `react-dom`
- `react-native-reanimated`
- `react-native-screens`
- `react-native-web`
- `react-native-worklets`
- `@types/react`

This does not necessarily mean these packages are unused. Some may provide platform support, type definitions, or functionality consumed indirectly by Expo and React Native libraries. They are flagged for further review rather than recommended for removal.

**Note:** This is a source-code import and configuration review, not a complete runtime dependency analysis. No package files were modified as part of this review.
