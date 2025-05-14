import { Box, Typography } from '@mui/material';

export default function Footer() {
    return (
        <Box
            component="footer"
            sx={{
                borderTop: '1px solid #e0e0e0',
                bgcolor: '#ffffff',
                py: 2,
                textAlign: 'center',
                mt: 'auto',
            }}
        >
            <Typography variant="caption" color="text.secondary">
                Conversor de Imagem • v1.0
            </Typography>
        </Box>
    );
}
