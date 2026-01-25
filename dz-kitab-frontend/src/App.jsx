import { Routes, Route, Navigate } from "react-router-dom";
import Layout from "./Layout";
import { Landingpage } from "./pages/LandingPage";
import Login from "./pages/Login";
import Register from "./pages/Register";
import { NotFound } from "./NotFound";
import AddAnnounce from "./pages/AddNewAnnounce";
import MyAnnouncements from "./pages/MyAnnouncements";
import Dashboard from "./pages/dashboard";
import Messages from "./pages/Messages";
import Listing from "./pages/Listing";
import Wishlist from "./pages/Wishlist";
import BookDetails from "./pages/BookDetails";
import AdminUsers from "./pages/Admin/UsersAdmin";
import AnnouncementsAdmin from "./pages/Admin/AnnouncementsAdmin";
import DashboardAdmin from "./pages/Admin/DashboardAdmin.jsx";
import Notifications from "./pages/Notifications";
import ContactSeller from "./pages/ContactSeller";
import "./style.css";
import { getCookie } from "./utils/cookies";

const PrivateRoute = ({ children }) => {
  const token = getCookie("access_token");
  return token ? children : <Navigate to="/login" />;
};

const PublicRoute = ({ children }) => {
  const token = getCookie("access_token");
  return !token ? children : <Navigate to="/" />;
};



export default function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route path="/" element={<Landingpage />} />

        <Route path="/login" element={
          <PublicRoute>
            <Login />
          </PublicRoute>
        } />

        {/* Admin Routes */}
        <Route path="/UsersAdmin" element={
          <PrivateRoute>
            <AdminUsers />
          </PrivateRoute>
        } />
        <Route path="/AnnouncementsAdmin" element={
          <PrivateRoute>
            <AnnouncementsAdmin />
          </PrivateRoute>
        } />
        <Route path="/DashboardAdmin" element={
          <PrivateRoute>
            <DashboardAdmin />
          </PrivateRoute>
        } />

        <Route path="/register" element={
          <PublicRoute>
            <Register />
          </PublicRoute>
        } />

        {/* User Routes */}
        <Route path="/addannounce" element={
          <PrivateRoute>
            <AddAnnounce />
          </PrivateRoute>
        } />
        <Route path="/dashboard" element={
          <PrivateRoute>
            <Dashboard />
          </PrivateRoute>
        } />
        <Route path="/message" element={
          <PrivateRoute>
            <Messages />
          </PrivateRoute>
        } />
        <Route path="/notifications" element={
          <PrivateRoute>
            <Notifications />
          </PrivateRoute>
        } />
        <Route path="/contact-seller" element={
          <PrivateRoute>
            <ContactSeller />
          </PrivateRoute>
        } />

        <Route path="/myannouncements" element={
          <PrivateRoute>
            <MyAnnouncements />
          </PrivateRoute>
        } />
        <Route path="/catalog" element={<Listing />} />
        <Route path="/wishlist" element={
          <PrivateRoute>
            <Wishlist />
          </PrivateRoute>
        } />
        <Route path="/book/:id" element={<BookDetails />} />
        <Route path="*" element={<NotFound />} />
      </Route>
    </Routes>
  );
}
