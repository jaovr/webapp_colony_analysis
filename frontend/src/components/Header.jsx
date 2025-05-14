import { AppBar, Toolbar, Typography, IconButton, Box } from '@mui/material';
import MenuIcon from '@mui/icons-material/Menu';
import InfoOutlinedIcon from '@mui/icons-material/InfoOutlined';

export default function Header({ toggleSidebar }) {
    return (
        <AppBar
            position="static"
            elevation={0}
            sx={{
                bgcolor: '#ffffff',
                borderBottom: '1px solid #e0e0e0',
                color: 'text.primary',
            }}
        >
            <Toolbar sx={{ justifyContent: 'space-between' }}>
                <Box display="flex" alignItems="center" gap={1}>
                    <IconButton onClick={toggleSidebar} size="small">
                        <MenuIcon fontSize="small" />
                    </IconButton>
                    <Typography variant="subtitle1" fontWeight={500}>
                        Processamento de Imagem
                    </Typography>
                </Box>

                <IconButton size="small">
                    <InfoOutlinedIcon fontSize="small" />
                </IconButton>
            </Toolbar>
        </AppBar>
    );
}

