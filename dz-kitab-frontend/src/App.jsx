import { Routes, Route } from "react-router-dom";
import Layout from "./Layout";
import { Landingpage } from "./pages/LandingPage";
import Login from './pages/Login'
import Register from './pages/Register'
import { NotFound } from "./NotFound";
import AddAnnounce from './pages/AddNewAnnounce'
import Messages from "./pages/Messages";
import "./App.css";
import './output.css'
export default function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route path="/" element={<Landingpage />} />
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route path="/addannounce" element={<AddAnnounce/>} />
        <Route path="/message" element={<Messages/>} />
        <Route path="*" element={<NotFound />} />
      </Route>
    </Routes>
  );
}
