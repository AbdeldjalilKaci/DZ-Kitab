import Footer from "./components/footer";
import Header from "./components/header";
import { Outlet, useLocation } from "react-router-dom";

export default function Layout() {
    const location = useLocation();

    const hideHeader =
        location.pathname !== "/" ;  

    return (
        <div className="layout">
            {hideHeader ? null : <Header />}
            <main>
                <Outlet />
            </main>
            {hideHeader ? null : <Footer />}
        </div>
    );
}
