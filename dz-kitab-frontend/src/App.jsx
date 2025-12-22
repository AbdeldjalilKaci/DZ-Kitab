import { Routes, Route } from "react-router-dom";
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
export default function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route path="/" element={<Landingpage />} />
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route path="/addannounce" element={<AddAnnounce />} />
        <Route path="/message" element={<Messages />} />
        <Route path="/catalog" element={<Listing />} />
        <Route path="/wishlist" element={<Wishlist />} />
        <Route path="/book/:id" element={<BookDetails />} />
        <Route path="*" element={<NotFound />} />
      </Route>
    </Routes>
  );
}