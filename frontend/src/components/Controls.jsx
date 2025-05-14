import {
    Box,
    Button,
    Typography,
    CircularProgress
} from '@mui/material';
import UploadFileIcon from '@mui/icons-material/UploadFile';
import TuneIcon from '@mui/icons-material/Tune';

export default function Controls({
                                     nomeArquivo,
                                     imagemOriginal,
                                     carregando,
                                     handleUpload,
                                     converterImagem
                                 }) {
    return (
        <Box
            display="flex"
            flexDirection="column"
            alignItems="center"
            gap={2}
            mt={2}
        >
            <input
                id="upload-input"
                type="file"
                accept="image/*"
                onChange={handleUpload}
                style={{ display: 'none' }}
            />

            <label htmlFor="upload-input">
                <Button
                    variant="outlined"
                    color="primary"
                    startIcon={<UploadFileIcon />}
                    component="span"
                >
                    {nomeArquivo || 'Selecionar imagem'}
                </Button>
            </label>

            <Button
                variant="outlined"
                color="secondary"
                onClick={converterImagem}
                disabled={!imagemOriginal || carregando}
                startIcon={carregando ? <CircularProgress size={18} /> : <TuneIcon />}
            >
                {carregando ? 'Processando...' : 'Converter imagem'}
            </Button>

            {nomeArquivo && (
                <Typography variant="caption" color="text.secondary">
                    Arquivo: {nomeArquivo}
                </Typography>
            )}
        </Box>
    );
}

