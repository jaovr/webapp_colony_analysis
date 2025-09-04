import { useState } from 'react'
import Header from './components/Header'
import ImagePanel from './components/ImagePanel'
import Controls from './components/Controls'
import Footer from './components/Footer'

export default function App() {
    const [selectedImage, setSelectedImage] = useState(null)
    const [processedImageUrl, setProcessedImageUrl] = useState(null)

    const handleConvert = async () => {
        if (!selectedImage) return
        const formData = new FormData()
        formData.append('imagem', selectedImage)
        const res = await fetch('http://localhost:8000/cinza/', {
            method: 'POST',
            body: formData,
        })
        if (!res.ok) {
            alert('Erro ao converter')
            return
        }
        const blob = await res.blob()
        setProcessedImageUrl(URL.createObjectURL(blob))
    }

    return (
        <div className="fixed top-0 left-0 w-full flex flex-col min-h-screen bg-base-100 text-base-content">
            <Header />

            <main className="flex-grow pt-16 px-4 flex  items-center">

                <div className="w-full space-y-8">
                    <ImagePanel
                        selectedImage={selectedImage}
                        processedImageUrl={processedImageUrl}
                    />
                    <Controls
                        onImageSelect={setSelectedImage}
                        onConvert={handleConvert}
                    />
                </div>
            </main>

            <Footer />
        </div>
    )
}


