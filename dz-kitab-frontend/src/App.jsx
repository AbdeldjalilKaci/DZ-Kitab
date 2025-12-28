import { Routes, Route, Navigate } from "react-router-dom";
import Layout from "./Layout";
import { Landingpage } from "./pages/LandingPage";
import Login from "./pages/Login";
import Register from "./pages/Register";
import { NotFound } from "./NotFound";
import AddAnnounce from "./pages/AddNewAnnounce";
import Messages from "./pages/Messages";
import Listing from "./pages/Listing";
import Wishlist from "./pages/Wishlist";
import BookDetails from "./pages/BookDetails";
import "./App.css";
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
        <Route path="/register" element={
          <PublicRoute>
            <Register />
          </PublicRoute>
        } />

        <Route path="/addannounce" element={
          <PrivateRoute>
            <AddAnnounce />
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
