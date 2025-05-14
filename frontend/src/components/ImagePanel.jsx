import { Box, Typography, Paper } from '@mui/material';
import ImageIcon from '@mui/icons-material/Image';

export default function ImagePanel({ titulo, imagem, carregando, vazioMsg }) {
    return (
        <Paper
            elevation={1}
            sx={{
                p: 3,
                width: '100%',
                maxWidth: 400,
                minHeight: 300,
                borderRadius: 3,
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                justifyContent: 'flex-start',
                gap: 2,
                bgcolor: 'background.paper',
            }}
        >
            <Typography variant="subtitle1" fontWeight={500}>
                {titulo}
            </Typography>

            {carregando ? (
                <Typography variant="body2" color="text.secondary">
                    Processando...
                </Typography>
            ) : imagem ? (
                <Box
                    component="img"
                    src={imagem}
                    alt={titulo}
                    sx={{ width: '100%', borderRadius: 2, objectFit: 'contain', maxHeight: 220 }}
                />
            ) : (
                <Box
                    display="flex"
                    flexDirection="column"
                    alignItems="center"
                    justifyContent="center"
                    sx={{ color: 'text.secondary', opacity: 0.6, mt: 2 }}
                >
                    <ImageIcon sx={{ fontSize: 40, mb: 1 }} />
                    <Typography variant="body2">{vazioMsg}</Typography>
                </Box>
            )}
        </Paper>
    );
}

