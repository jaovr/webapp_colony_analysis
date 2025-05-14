import { useState } from 'react';
import Header from './components/Header';
import Footer from './components/Footer';
import Controls from './components/Controls';
import ImagePanel from './components/ImagePanel';
import { Box, Container } from '@mui/material';

export default function App() {
    const [imagemOriginal, setImagemOriginal] = useState(null);
    const [imagemConvertida, setImagemConvertida] = useState(null);
    const [nomeArquivo, setNomeArquivo] = useState('');
    const [carregando, setCarregando] = useState(false);

    const handleUpload = (e) => {
        const file = e.target.files[0];
        if (file) {
            const url = URL.createObjectURL(file);
            setImagemOriginal(url);
            setImagemConvertida(null);
            setNomeArquivo(file.name);
        }
    };

    const converterImagem = () => {
        if (!imagemOriginal) return;
        setCarregando(true);
        setTimeout(() => {
            setImagemConvertida(imagemOriginal);
            setCarregando(false);
        }, 1500);
    };

    return (
        <Box display="flex" flexDirection="column" minHeight="100vh" bgcolor="background.default">
            <Header toggleSidebar={() => {}} />

            <Box component="main" flex={1} py={6}>
                <Container maxWidth="lg">
                    {/* Painéis de imagem */}
                    <Box
                        display="flex"
                        gap={4}
                        flexWrap="wrap"
                        justifyContent="center"
                        mb={5}
                    >
                        <ImagePanel
                            titulo="Original"
                            imagem={imagemOriginal}
                            carregando={false}
                            vazioMsg="Nenhuma imagem original selecionada."
                        />
                        <ImagePanel
                            titulo="Resultado"
                            imagem={imagemConvertida}
                            carregando={carregando}
                            vazioMsg="Nenhuma imagem convertida."
                        />
                    </Box>

                    {/* Botões abaixo */}
                    <Box display="flex" justifyContent="center">
                        <Controls
                            nomeArquivo={nomeArquivo}
                            imagemOriginal={imagemOriginal}
                            carregando={carregando}
                            handleUpload={handleUpload}
                            converterImagem={converterImagem}
                        />
                    </Box>
                </Container>
            </Box>

            <Footer />
        </Box>
    );
}

