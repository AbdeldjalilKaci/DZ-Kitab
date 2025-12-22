import Footer from "./components/footer";
import Header from "./components/header";
import { Outlet, useLocation } from "react-router-dom";
import "./style.css";
import "../src/style.css";
import "./App.css";
export default function Layout() {
    const location = useLocation();

    const hideOnPages = [
        "*",
        "/login", 
        "/register", 
    ];

    const shouldHide = hideOnPages.includes(location.pathname);

    return (
        <div className="layout">
            {!shouldHide && <Header />}
            <main className={shouldHide ? "full-height" : ""}>
                <Outlet />
            </main>
            {!shouldHide && <Footer />}
        </div>
    );
}