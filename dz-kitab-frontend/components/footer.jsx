import React from 'react'

const Footer = () => {
    return (
        <footer className='footer' >
            <h1><span>DZ</span>-Kitab</h1>
            <div className="footer-content">
                <div className="">
                    <h3>Support</h3>
                    <ul>
                        <li>FAQ</li>
                        <li>Centre d’aide</li>
                        <li>Nous contacter</li>
                    </ul>
                </div>
                <div className="">
                    <h3>Legel</h3>
                    <ul>
                        <li>Confidentialité</li>
                        <li>Conditions d’utilisation</li>
                        <li>Mentions légales</li>
                    </ul>
                </div>
                <div className="">
                    <h3>Contact</h3>
                    <ul>
                        <li>support@dz-kitab.dz</li>
                        <li>+213 123 456 789</li>
                        <li>alger,algérie</li>
                    </ul>
                </div>
                <div className="">
                    <h3>Suivie-nous</h3>
                    <ul>
                        <li>Facebook</li>
                        <li>Instagrlime</li>
                        <li>Twitter</li>
                        <li>linkedIn</li>
                    </ul>
                </div>
                
            </div>
            <hr></hr>
            <p>© 2024 DZ-Kitab. Tous droits réservés. La révolution du livre en algérie.</p>
        </footer>
    )
}

export default Footer