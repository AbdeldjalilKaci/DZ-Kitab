import { Routes, Route } from "react-router-dom";
import Layout from "./Layout";
import { Landingpage } from "./pages/LandingPage";
import { NotFound } from "./NotFound";
import './App.css'
export default function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route path="/" element={<Landingpage />} />
        <Route path="*" element={<NotFound />} />
      </Route>
    </Routes>
  );
}
