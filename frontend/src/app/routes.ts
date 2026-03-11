import { createBrowserRouter } from "react-router";
import { MainPage } from "./pages/MainPage";
import { ProfilePage } from "./pages/ProfilePage";
import { ScanPage } from "./pages/ScanPage";
import { ResultPage } from "./pages/ResultPage";
import { SettingsPage } from "./pages/SettingsPage";
import { ReportPage } from "./pages/ReportPage";
import { InfoPage } from "./pages/InfoPage";
import { HistoryPage } from "./pages/HistoryPage";

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
  {
    path: "/report",
    Component: ReportPage,
  },
  {
    path: "/info",
    Component: InfoPage,
  },
]);
