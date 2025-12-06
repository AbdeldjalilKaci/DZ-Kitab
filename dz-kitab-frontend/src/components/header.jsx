import React from 'react'
import { Button } from './button'
const Header = () => {
    return (
        <header>
            <div className="website-title">
                <img className='logo' src='./dz-kitablogo.png'></img>
                <a className="a"><h3><span>DZ</span>-KITAB</h3></a>
            </div>
            <div className="links">
                <a>Home</a>
                <a>About us</a>
                <a>Contact us</a>
            </div>
            <div className="buttons">
                <button className='login-button'>Login</button>
                <button className='register-button'>Register</button>
            </div>
        </header>
    )
}

export default Header