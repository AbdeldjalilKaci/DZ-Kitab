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
        <Route path="/UsersAdmin" element={
          <PublicRoute>
            <AdminUsers />
          </PublicRoute>
        } />
         <Route path="/AnnouncementsAdmin" element={
          <PublicRoute>
            <AnnouncementsAdmin />
          </PublicRoute>
        } />
        <Route path="/register" element={
          <PublicRoute>
            <Register />
          </PublicRoute>
        } />
         <Route path="/MyAnnouncements" element={
          <PrivateRoute>
            <MyAnnouncements />
          </PrivateRoute>
        } />
        <Route path="/DashboardAdmin" element={
          <PublicRoute>
            <DashboardAdmin />
          </PublicRoute>
        } />

        <Route path="/addannounce" element={
          <PrivateRoute>
            <AddAnnounce />
          </PrivateRoute>
        } />
        <Route path="/dashboard" element={
          <PrivateRoute>
            <Dashboard/>
          </PrivateRoute>
        } />
        <Route path="/message" element={
          <PrivateRoute>
            <Messages />
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
