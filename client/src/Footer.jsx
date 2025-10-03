import React from 'react'
import { Link } from 'react-router-dom'
import { MdTranslate } from 'react-icons/md'

const Footer = () => {
    return (
        <footer className="bg-gray-900 text-white py-8">
            <div className="max-w-7xl mx-auto px-4">
                <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
                    <div className="md:col-span-2">
                        <div className="flex items-center space-x-3 mb-4">
                            <div className="bg-gradient-to-r from-blue-500 to-purple-500 p-2 rounded-lg">
                                <MdTranslate className="w-8 h-8 text-white" />
                            </div>
                            <span className="text-2xl font-bold">SignSpeak</span>
                        </div>
                        <p className="text-gray-400 mb-4">
                            Breaking down communication barriers with AI-powered sign language translation technology.
                        </p>
                    </div>
                    <div>
                        <h3 className="text-lg font-semibold mb-4">Quick Links</h3>
                        <ul className="space-y-2">
                            <li><Link to="/" className="text-gray-400 hover:text-white transition-colors">Home</Link></li>
                            <li><Link to="/sign2text" className="text-gray-400 hover:text-white transition-colors">Translate</Link></li>
                            <li><a href="#features" className="text-gray-400 hover:text-white transition-colors">Features</a></li>
                            <li><a href="#about" className="text-gray-400 hover:text-white transition-colors">About</a></li>
                        </ul>
                    </div>
                    <div>
                        <h3 className="text-lg font-semibold mb-4">Support</h3>
                        <ul className="space-y-2">
                            <li><a href="#" className="text-gray-400 hover:text-white transition-colors">Help Center</a></li>
                            <li><a href="#" className="text-gray-400 hover:text-white transition-colors">Contact Us</a></li>
                            <li><a href="#" className="text-gray-400 hover:text-white transition-colors">Privacy Policy</a></li>
                            <li><a href="#" className="text-gray-400 hover:text-white transition-colors">Terms of Service</a></li>
                        </ul>
                    </div>
                </div>
                <div className="border-t border-gray-800 mt-8 pt-8 text-center">
                    <p className="text-gray-400">
                        © 2025 SignSpeak. All rights reserved. Made with ❤️ for accessibility.
                    </p>
                </div>
            </div>
        </footer>
    )
}

export default Footer
