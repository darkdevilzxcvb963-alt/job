import React from 'react';
import { Link } from 'react-router-dom';
import { Mail, Github, Twitter, Linkedin, ExternalLink } from 'lucide-react';
import '../styles/Footer.css';

const Footer = () => {
    return (
        <footer className="footer">
            <div className="footer-glow"></div>
            <div className="footer-content">
                <div className="footer-grid">
                    <div className="footer-brand">
                        <h2 className="footer-logo">Career<span className="accent">OS</span></h2>
                        <p>Empowering the next generation of talent through AI-driven intelligence and seamless matching.</p>
                        <div className="social-links">
                            <a href="#" className="social-icon"><Twitter size={18} /></a>
                            <a href="#" className="social-icon"><Github size={18} /></a>
                            <a href="#" className="social-icon"><Linkedin size={18} /></a>
                        </div>
                    </div>

                    <div className="footer-links">
                        <h4>Platform</h4>
                        <ul>
                            <li><Link to="/login">AI Engine</Link></li>
                            <li><Link to="/login">Matches</Link></li>
                            <li><Link to="/login">Job Board</Link></li>
                            <li><Link to="/login">Pricing</Link></li>
                        </ul>
                    </div>

                    <div className="footer-links">
                        <h4>Resources</h4>
                        <ul>
                            <li><Link to="/login">Documentation</Link></li>
                            <li><Link to="/login">API Reference</Link></li>
                            <li><Link to="/login">Guides</Link></li>
                            <li><Link to="/login">Support</Link></li>
                        </ul>
                    </div>

                    <div className="footer-links">
                        <h4>Company</h4>
                        <ul>
                            <li><Link to="/login">About Us</Link></li>
                            <li><Link to="/login">Careers</Link></li>
                            <li><Link to="/login">Privacy Policy</Link></li>
                            <li><Link to="/login">Terms of Service</Link></li>
                        </ul>
                    </div>
                </div>

                <div className="footer-bottom">
                    <p>&copy; 2026 Career OS. Built with passion for the future of work.</p>
                    <div className="footer-meta">
                        <span>System Status: <span className="status-online">Operational</span></span>
                        <span className="divider">|</span>
                        <a href="#" className="tech-stack">Tech Stack <ExternalLink size={12} /></a>
                    </div>
                </div>
            </div>
        </footer>
    );
};

export default Footer;
