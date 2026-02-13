import { createBrowserRouter } from "react-router";
import { MainPage } from "./pages/MainPage";
import { ProfilePage } from "./pages/ProfilePage";
import { ScanPage } from "./pages/ScanPage";
import { ResultPage } from "./pages/ResultPage";
import { SettingsPage } from "./pages/SettingsPage";

export const router = createBrowserRouter([
  {
    path: "/",
    Component: MainPage,
  },
  {
    path: "/profile",
    Component: ProfilePage,
  },
  {
    path: "/scan",
    Component: ScanPage,
  },
  {
    path: "/result",
    Component: ResultPage,
  },
  {
    path: "/settings",
    Component: SettingsPage,
  },
]);
