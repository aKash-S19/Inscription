import { Routes, Route } from 'react-router-dom'
import Navbar from './components/Navbar'
import Footer from './components/Footer'
import Home from './pages/Home'
import TempleGallery from './pages/TempleGallery'
import TempleDetails from './pages/TempleDetails'
import InscriptionExplorer from './pages/InscriptionExplorer'
import InscriptionDetails from './pages/InscriptionDetails'
import InteractiveMap from './pages/InteractiveMap'
import Explore from './pages/Explore'
import Timeline from './pages/Timeline'
import About from './pages/About'
import AiLab from './pages/AiLab'

export default function App() {
  return (
    <div className="flex min-h-screen flex-col">
      <Navbar />
      <main className="flex-1">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/temples" element={<TempleGallery />} />
          <Route path="/temples/:slug" element={<TempleDetails />} />
          <Route path="/inscriptions" element={<InscriptionExplorer />} />
          <Route path="/inscriptions/:slug" element={<InscriptionDetails />} />
          <Route path="/map" element={<InteractiveMap />} />
          <Route path="/explore" element={<Explore />} />
          <Route path="/timeline" element={<Timeline />} />
          <Route path="/about" element={<About />} />
          <Route path="/ai" element={<AiLab />} />
        </Routes>
      </main>
      <Footer />
    </div>
  )
}
