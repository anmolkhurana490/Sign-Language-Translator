import { Routes, Route } from 'react-router-dom'
import Home from './Home'
import Sign2Text from './Sign2Text'
import Navbar from './Navbar'
import Footer from './Footer'
import './App.css'

function App() {
  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />

      <Routes>
        <Route path='/' element={<Home />} />
        <Route path='/sign2text' element={<Sign2Text />} />
      </Routes>

      <Footer />
    </div>
  )
}

export default App
