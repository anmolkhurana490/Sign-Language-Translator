import React, { useState } from 'react'
import { Link, useLocation } from 'react-router-dom'
import { HiMenu, HiX } from 'react-icons/hi'
import { MdTranslate } from 'react-icons/md'

const Navbar = () => {
    const [isMenuOpen, setIsMenuOpen] = useState(false)
    const location = useLocation()

    const isActive = (path) => location.pathname === path

    return (
        <nav className="bg-gradient-to-r from-blue-600 via-purple-600 to-indigo-700 shadow-lg sticky top-0 z-50">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                <div className="flex justify-between items-center h-16">
                    {/* Logo */}
                    <div className="flex items-center">
                        <Link to="/" className="flex items-center space-x-3">
                            <div className="bg-white p-2 rounded-lg">
                                <MdTranslate className="w-8 h-8 text-blue-600" />
                            </div>
                            <span className="text-white font-bold text-xl">SignSpeak</span>
                        </Link>
                    </div>

                    {/* Desktop Navigation */}
                    <div className="hidden md:block">
                        <div className="ml-10 flex items-baseline space-x-4">
                            <Link
                                to="/"
                                className={`px-3 py-2 rounded-md text-sm font-medium transition-colors duration-200 ${isActive('/')
                                    ? 'bg-white/20 text-white'
                                    : 'text-white/80 hover:bg-white/10 hover:text-white'
                                    }`}
                            >
                                Home
                            </Link>
                            <Link
                                to="/sign2text"
                                className={`px-3 py-2 rounded-md text-sm font-medium transition-colors duration-200 ${isActive('/sign2text')
                                    ? 'bg-white/20 text-white'
                                    : 'text-white/80 hover:bg-white/10 hover:text-white'
                                    }`}
                            >
                                Translate
                            </Link>
                            <a
                                href="/#features"
                                className="text-white/80 hover:bg-white/10 hover:text-white px-3 py-2 rounded-md text-sm font-medium transition-colors duration-200"
                            >
                                Features
                            </a>
                            <a
                                href="/#about"
                                className="text-white/80 hover:bg-white/10 hover:text-white px-3 py-2 rounded-md text-sm font-medium transition-colors duration-200"
                            >
                                About
                            </a>
                        </div>
                    </div>

                    {/* Mobile menu button */}
                    <div className="md:hidden">
                        <button
                            onClick={() => setIsMenuOpen(!isMenuOpen)}
                            className="bg-white/10 inline-flex items-center justify-center p-2 rounded-md text-white hover:text-white hover:bg-white/20 focus:outline-none focus:ring-2 focus:ring-inset focus:ring-white"
                        >
                            <span className="sr-only">Open main menu</span>
                            {!isMenuOpen ? (
                                <HiMenu className="block h-6 w-6" />
                            ) : (
                                <HiX className="block h-6 w-6" />
                            )}
                        </button>
                    </div>
                </div>
            </div>

            {/* Mobile Navigation Menu */}
            {isMenuOpen && (
                <div className="md:hidden">
                    <div className="px-2 pt-2 pb-3 space-y-1 sm:px-3 bg-black/20">
                        <Link
                            to="/"
                            className={`block px-3 py-2 rounded-md text-base font-medium transition-colors duration-200 ${isActive('/')
                                ? 'bg-white/20 text-white'
                                : 'text-white/80 hover:bg-white/10 hover:text-white'
                                }`}
                            onClick={() => setIsMenuOpen(false)}
                        >
                            Home
                        </Link>
                        <Link
                            to="/sign2text"
                            className={`block px-3 py-2 rounded-md text-base font-medium transition-colors duration-200 ${isActive('/sign2text')
                                ? 'bg-white/20 text-white'
                                : 'text-white/80 hover:bg-white/10 hover:text-white'
                                }`}
                            onClick={() => setIsMenuOpen(false)}
                        >
                            Translate
                        </Link>
                        <a
                            href="#features"
                            className="text-white/80 hover:bg-white/10 hover:text-white block px-3 py-2 rounded-md text-base font-medium transition-colors duration-200"
                            onClick={() => setIsMenuOpen(false)}
                        >
                            Features
                        </a>
                        <a
                            href="#about"
                            className="text-white/80 hover:bg-white/10 hover:text-white block px-3 py-2 rounded-md text-base font-medium transition-colors duration-200"
                            onClick={() => setIsMenuOpen(false)}
                        >
                            About
                        </a>
                    </div>
                </div>
            )}
        </nav>
    )
}

export default Navbar
