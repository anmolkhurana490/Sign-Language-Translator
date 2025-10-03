import React from 'react'
import { Link } from 'react-router-dom'
import {
    FaPlay,
    FaBolt,
    FaCheckCircle,
    FaMobileAlt,
    FaClock,
    FaShieldAlt,
    FaChartLine,
    FaStar
} from 'react-icons/fa'

const Home = () => {
    return (
        <div className="min-h-screen">
            {/* Hero Section */}
            <section className="relative bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50 py-20 px-4 overflow-hidden">
                <div className="absolute inset-0 bg-gradient-to-r from-blue-600/10 to-purple-600/10"></div>
                <div className="relative max-w-7xl mx-auto">
                    <div className="text-center">
                        <h1 className="text-4xl sm:text-5xl md:text-6xl font-bold text-gray-900 mb-6 leading-tight">
                            Bridge Communication with
                            <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-purple-600"> AI-Powered </span>
                            Sign Language Translation
                        </h1>
                        <p className="text-xl text-gray-600 mb-8 max-w-3xl mx-auto leading-relaxed">
                            Experience seamless communication with our cutting-edge AI technology that translates
                            sign language gestures into text in real-time, making conversations more accessible than ever.
                        </p>
                        <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
                            <Link
                                to="/sign2text"
                                className="bg-gradient-to-r from-blue-600 to-purple-600 text-white px-8 py-4 rounded-full font-semibold text-lg hover:from-blue-700 hover:to-purple-700 transform hover:scale-105 transition-all duration-200 shadow-lg hover:shadow-xl"
                            >
                                Start Translating Now
                            </Link>
                            <a href='#demo-video' className="border-2 border-gray-300 text-gray-700 px-8 py-4 rounded-full font-semibold text-lg hover:border-gray-400 hover:bg-gray-50 transition-all duration-200">
                                Watch Demo
                            </a>
                        </div>
                    </div>

                    {/* Hero Image/Video Placeholder */}
                    <div className="mt-16 max-w-4xl mx-auto" id="demo-video">
                        <div className="bg-white rounded-2xl shadow-2xl p-8 border border-gray-200">
                            <div className="aspect-video bg-gradient-to-br from-gray-100 to-gray-200 rounded-xl flex items-center justify-center relative overflow-hidden">
                                <video
                                    className="w-full h-full object-cover rounded-xl"
                                    controls muted
                                    // poster="/demo-thumbnail.jpg"
                                    onError={(e) => {
                                        e.target.style.display = 'none';
                                        e.target.nextElementSibling.style.display = 'flex';
                                    }}
                                >
                                    <source src="/demo-video.mp4" type="video/mp4" />
                                    Your browser does not support the video tag.
                                </video>

                                {/* Fallback placeholder when video is not available */}
                                <div className="absolute inset-0 flex items-center justify-center text-center" style={{ display: 'none' }}>
                                    <div>
                                        <div className="w-20 h-20 bg-gradient-to-r from-blue-500 to-purple-500 rounded-full flex items-center justify-center mx-auto mb-4">
                                            <FaPlay className="w-10 h-10 text-white" />
                                        </div>
                                        <p className="text-gray-500 font-medium">Interactive Demo Coming Soon</p>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </section>

            {/* Features Section */}
            <section id="features" className="py-20 bg-white">
                <div className="max-w-7xl mx-auto px-4">
                    <div className="text-center mb-16">
                        <h2 className="text-3xl sm:text-4xl font-bold text-gray-900 mb-4">
                            Powerful Features for Everyone
                        </h2>
                        <p className="text-xl text-gray-600 max-w-2xl mx-auto">
                            Our advanced AI technology makes sign language translation accessible, accurate, and easy to use.
                        </p>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
                        {/* Feature 1 */}
                        <div className="group bg-gradient-to-br from-blue-50 to-indigo-50 p-8 rounded-2xl hover:shadow-lg transition-all duration-300 border border-blue-100">
                            <div className="w-16 h-16 bg-gradient-to-r from-blue-500 to-indigo-500 rounded-xl flex items-center justify-center mb-6 group-hover:scale-110 transition-transform duration-300">
                                <FaBolt className="w-8 h-8 text-white" />
                            </div>
                            <h3 className="text-xl font-semibold text-gray-900 mb-3">Real-time Translation</h3>
                            <p className="text-gray-600 leading-relaxed">
                                Instant sign language to text conversion with minimal latency for natural conversations.
                            </p>
                        </div>

                        {/* Feature 2 */}
                        <div className="group bg-gradient-to-br from-purple-50 to-pink-50 p-8 rounded-2xl hover:shadow-lg transition-all duration-300 border border-purple-100">
                            <div className="w-16 h-16 bg-gradient-to-r from-purple-500 to-pink-500 rounded-xl flex items-center justify-center mb-6 group-hover:scale-110 transition-transform duration-300">
                                <FaCheckCircle className="w-8 h-8 text-white" />
                            </div>
                            <h3 className="text-xl font-semibold text-gray-900 mb-3">High Accuracy</h3>
                            <p className="text-gray-600 leading-relaxed">
                                Advanced machine learning models trained on extensive datasets for precise recognition.
                            </p>
                        </div>

                        {/* Feature 3 */}
                        <div className="group bg-gradient-to-br from-green-50 to-emerald-50 p-8 rounded-2xl hover:shadow-lg transition-all duration-300 border border-green-100">
                            <div className="w-16 h-16 bg-gradient-to-r from-green-500 to-emerald-500 rounded-xl flex items-center justify-center mb-6 group-hover:scale-110 transition-transform duration-300">
                                <FaMobileAlt className="w-8 h-8 text-white" />
                            </div>
                            <h3 className="text-xl font-semibold text-gray-900 mb-3">Mobile Friendly</h3>
                            <p className="text-gray-600 leading-relaxed">
                                Works seamlessly across all devices - desktop, tablet, and mobile phones.
                            </p>
                        </div>

                        {/* Feature 4 */}
                        <div className="group bg-gradient-to-br from-orange-50 to-red-50 p-8 rounded-2xl hover:shadow-lg transition-all duration-300 border border-orange-100">
                            <div className="w-16 h-16 bg-gradient-to-r from-orange-500 to-red-500 rounded-xl flex items-center justify-center mb-6 group-hover:scale-110 transition-transform duration-300">
                                <FaClock className="w-8 h-8 text-white" />
                            </div>
                            <h3 className="text-xl font-semibold text-gray-900 mb-3">24/7 Availability</h3>
                            <p className="text-gray-600 leading-relaxed">
                                Access our translation service anytime, anywhere without any downtime.
                            </p>
                        </div>

                        {/* Feature 5 */}
                        <div className="group bg-gradient-to-br from-teal-50 to-cyan-50 p-8 rounded-2xl hover:shadow-lg transition-all duration-300 border border-teal-100">
                            <div className="w-16 h-16 bg-gradient-to-r from-teal-500 to-cyan-500 rounded-xl flex items-center justify-center mb-6 group-hover:scale-110 transition-transform duration-300">
                                <FaShieldAlt className="w-8 h-8 text-white" />
                            </div>
                            <h3 className="text-xl font-semibold text-gray-900 mb-3">Privacy First</h3>
                            <p className="text-gray-600 leading-relaxed">
                                Your data stays secure with end-to-end encryption and privacy protection.
                            </p>
                        </div>

                        {/* Feature 6 */}
                        <div className="group bg-gradient-to-br from-violet-50 to-purple-50 p-8 rounded-2xl hover:shadow-lg transition-all duration-300 border border-violet-100">
                            <div className="w-16 h-16 bg-gradient-to-r from-violet-500 to-purple-500 rounded-xl flex items-center justify-center mb-6 group-hover:scale-110 transition-transform duration-300">
                                <FaChartLine className="w-8 h-8 text-white" />
                            </div>
                            <h3 className="text-xl font-semibold text-gray-900 mb-3">Continuous Learning</h3>
                            <p className="text-gray-600 leading-relaxed">
                                Our AI models continuously improve with user feedback and new data.
                            </p>
                        </div>
                    </div>
                </div>
            </section>

            {/* About Section */}
            <section id="about" className="py-20 bg-gradient-to-br from-gray-50 to-blue-50">
                <div className="max-w-7xl mx-auto px-4">
                    <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
                        <div>
                            <h2 className="text-3xl sm:text-4xl font-bold text-gray-900 mb-6">
                                Making Communication
                                <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-purple-600"> Universal</span>
                            </h2>
                            <p className="text-lg text-gray-600 mb-6 leading-relaxed">
                                Our mission is to break down communication barriers by leveraging artificial intelligence
                                to translate sign language in real-time. We believe that everyone deserves to be heard
                                and understood, regardless of their preferred method of communication.
                            </p>
                            <p className="text-lg text-gray-600 mb-8 leading-relaxed">
                                Built with cutting-edge computer vision and machine learning technologies, our platform
                                recognizes hand gestures and converts them to text instantly, creating a bridge between
                                the deaf and hearing communities.
                            </p>
                            <div className="flex flex-col sm:flex-row gap-4">
                                <Link
                                    to="/sign2text"
                                    className="bg-gradient-to-r from-blue-600 to-purple-600 text-white px-6 py-3 rounded-lg font-semibold hover:from-blue-700 hover:to-purple-700 transform hover:scale-105 transition-all duration-200 text-center"
                                >
                                    Try It Now
                                </Link>
                                <button className="border-2 border-gray-300 text-gray-700 px-6 py-3 rounded-lg font-semibold hover:border-gray-400 hover:bg-gray-50 transition-all duration-200">
                                    Learn More
                                </button>
                            </div>
                        </div>
                        <div className="lg:pl-8">
                            <div className="bg-white rounded-2xl shadow-xl p-8 border border-gray-200">
                                <div className="aspect-square bg-gradient-to-br from-blue-100 via-purple-100 to-indigo-100 rounded-xl flex items-center justify-center">
                                    <div className="text-center">
                                        <div className="w-24 h-24 bg-gradient-to-r from-blue-500 to-purple-500 rounded-full flex items-center justify-center mx-auto mb-6">
                                            <FaStar className="w-12 h-12 text-white" />
                                        </div>
                                        <h3 className="text-xl font-semibold text-gray-900 mb-2">Empowering Communication</h3>
                                        <p className="text-gray-600">Bringing people together through technology</p>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </section>

            {/* CTA Section */}
            <section className="py-20 bg-gradient-to-r from-blue-600 to-purple-600">
                <div className="max-w-4xl mx-auto text-center px-4">
                    <h2 className="text-3xl sm:text-4xl font-bold text-white mb-6">
                        Ready to Start Translating?
                    </h2>
                    <p className="text-xl text-blue-100 mb-8 max-w-2xl mx-auto">
                        Join thousands of users who are already breaking communication barriers with our AI-powered sign language translator.
                    </p>
                    <Link
                        to="/sign2text"
                        className="inline-block bg-white text-blue-600 px-8 py-4 rounded-full font-semibold text-lg hover:bg-gray-100 transform hover:scale-105 transition-all duration-200 shadow-lg hover:shadow-xl"
                    >
                        Get Started for Free
                    </Link>
                </div>
            </section>
        </div>
    )
}

export default Home