/**
 * Główny layout aplikacji
 * Zawiera nawigację, strukturę strony i kontener na treść
 */
import React, { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import {
  AppBar,
  Box,
  Container,
  Drawer,
  IconButton,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Toolbar,
  Typography,
  Divider,
  useTheme,
  useMediaQuery,
  Avatar,
  Menu,
  MenuItem,
  Badge,
  Tooltip,
} from '@mui/material';
import {
  Menu as MenuIcon,
  Chat as ChatIcon,
  Settings as SettingsIcon,
  Notifications as NotificationsIcon,
  AccountCircle as AccountCircleIcon,
  ChevronLeft as ChevronLeftIcon,
  Psychology as PsychologyIcon,
  Dashboard as DashboardIcon,
  Person as PersonIcon,
  School as SchoolIcon,
} from '@mui/icons-material';

// Szerokość szuflady nawigacyjnej
const drawerWidth = 260;

// Elementy menu nawigacyjnego
const menuItems = [
  {
    text: 'Dashboard',
    icon: <DashboardIcon />,
    path: '/',
  },
  {
    text: 'Klienci',
    icon: <PersonIcon />,
    path: '/clients',
  },
  {
    text: 'Demo: Quick Response',
    icon: <ChatIcon />,
    path: '/demo/interactions',
    badge: { content: 'DEMO', color: 'primary' },
  },
  {
    text: 'Zarządzanie Wiedzą',
    icon: <PsychologyIcon />,
    path: '/admin/knowledge',
    badge: { content: 'ADMIN', color: 'warning' },
  },
  {
    text: 'AI Dojo: Sparing z Mistrzem',
    icon: <SchoolIcon />,
    path: '/admin/dojo',
    badge: { content: 'MODUŁ 3', color: 'secondary' },
  },
  {
    text: 'Ustawienia',
    icon: <SettingsIcon />,
    path: '/settings',
  },
];

const MainLayout = ({ children, title = 'AI Sales Co-Pilot' }) => {
  const theme = useTheme();
  const location = useLocation();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  const [mobileOpen, setMobileOpen] = useState(false);
  const [anchorEl, setAnchorEl] = useState(null);
  const [notificationAnchor, setNotificationAnchor] = useState(null);

  // Toggle dla mobilnej szuflady
  const handleDrawerToggle = () => {
    setMobileOpen(!mobileOpen);
  };

  // Menu użytkownika
  const handleProfileMenuOpen = (event) => {
    setAnchorEl(event.currentTarget);
  };

  const handleProfileMenuClose = () => {
    setAnchorEl(null);
  };

  // Menu notyfikacji
  const handleNotificationMenuOpen = (event) => {
    setNotificationAnchor(event.currentTarget);
  };

  const handleNotificationMenuClose = () => {
    setNotificationAnchor(null);
  };

  // Zawartość szuflady nawigacyjnej
  const drawerContent = (
    <Box>
      {/* Logo i nazwa aplikacji */}
      <Box
        sx={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          p: 2,
          minHeight: 64,
        }}
      >
        <Box 
          component={Link}
          to="/"
          sx={{ 
            display: 'flex', 
            alignItems: 'center', 
            gap: 1,
            textDecoration: 'none',
            color: 'inherit',
          }}
        >
          <PsychologyIcon sx={{ color: 'primary.main', fontSize: 32 }} />
          <Box>
            <Typography variant="h6" sx={{ fontWeight: 700, lineHeight: 1.2 }}>
              Sales Co-Pilot
            </Typography>
            <Typography variant="caption" sx={{ color: 'text.secondary' }}>
              AI Assistant v0.2
            </Typography>
          </Box>
        </Box>
        {isMobile && (
          <IconButton onClick={handleDrawerToggle} size="small">
            <ChevronLeftIcon />
          </IconButton>
        )}
      </Box>

      <Divider />

      {/* Menu nawigacyjne */}
      <List sx={{ px: 1, py: 2 }}>
        {menuItems.map((item) => {
          const isActive = location.pathname === item.path || 
                          (item.path === '/clients' && location.pathname.startsWith('/clients'));
          
          return (
            <ListItem key={item.text} disablePadding sx={{ mb: 0.5 }}>
              <ListItemButton
                component={Link}
                to={item.path}
                selected={isActive}
                sx={{
                  borderRadius: 2,
                  textDecoration: 'none',
                  color: 'inherit',
                  '&:hover': {
                    backgroundColor: 'action.hover',
                  },
                  '&.Mui-selected': {
                    backgroundColor: 'primary.main',
                    color: 'primary.contrastText',
                    '& .MuiListItemIcon-root': {
                      color: 'primary.contrastText',
                    },
                    '&:hover': {
                      backgroundColor: 'primary.dark',
                    },
                  },
                }}
              >
                <ListItemIcon sx={{ minWidth: 40 }}>
                  {item.badge ? (
                    <Badge
                      badgeContent={item.badge.content}
                      color={item.badge.color}
                      variant="dot"
                    >
                      {item.icon}
                    </Badge>
                  ) : (
                    item.icon
                  )}
                </ListItemIcon>
                <ListItemText
                  primary={item.text}
                  primaryTypographyProps={{
                    fontSize: '0.9rem',
                    fontWeight: 500,
                  }}
                />
              </ListItemButton>
            </ListItem>
          );
        })}
      </List>

      <Divider />

      {/* Ustawienia */}
      <List sx={{ px: 1, py: 2 }}>
        <ListItem disablePadding>
          <ListItemButton 
            component={Link}
            to="/settings"
            sx={{ 
              borderRadius: 2,
              textDecoration: 'none',
              color: 'inherit',
            }}
          >
            <ListItemIcon sx={{ minWidth: 40 }}>
              <SettingsIcon />
            </ListItemIcon>
            <ListItemText
              primary="Ustawienia"
              primaryTypographyProps={{
                fontSize: '0.9rem',
                fontWeight: 500,
              }}
            />
          </ListItemButton>
        </ListItem>
      </List>
    </Box>
  );

  return (
    <Box sx={{ display: 'flex' }}>
      {/* AppBar - górna belka */}
      <AppBar
        position="fixed"
        sx={{
          width: { md: `calc(100% - ${drawerWidth}px)` },
          ml: { md: `${drawerWidth}px` },
        }}
      >
        <Toolbar>
          {/* Przycisk menu na mobile */}
          {isMobile && (
            <IconButton
              color="inherit"
              aria-label="open drawer"
              edge="start"
              onClick={handleDrawerToggle}
              sx={{ mr: 2 }}
            >
              <MenuIcon />
            </IconButton>
          )}

          {/* Tytuł strony */}
          <Typography variant="h6" noWrap component="div" sx={{ flexGrow: 1, fontWeight: 600 }}>
            {title}
          </Typography>

          {/* Przyciski akcji */}
          <Box sx={{ display: 'flex', gap: 1, alignItems: 'center' }}>
            {/* Notyfikacje */}
            <Tooltip title="Notyfikacje">
              <IconButton
                size="large"
                color="inherit"
                onClick={handleNotificationMenuOpen}
              >
                <Badge badgeContent={3} color="error">
                  <NotificationsIcon />
                </Badge>
              </IconButton>
            </Tooltip>

            {/* Menu notyfikacji */}
            <Menu
              anchorEl={notificationAnchor}
              open={Boolean(notificationAnchor)}
              onClose={handleNotificationMenuClose}
              PaperProps={{
                sx: { width: 320, maxHeight: 400 },
              }}
            >
              <Box sx={{ p: 2 }}>
                <Typography variant="h6">Notyfikacje</Typography>
              </Box>
              <Divider />
              <MenuItem onClick={handleNotificationMenuClose}>
                <Typography variant="body2">
                  <strong>Nowa sesja</strong> - Klient Jan Kowalski rozpoczął rozmowę
                </Typography>
              </MenuItem>
              <MenuItem onClick={handleNotificationMenuClose}>
                <Typography variant="body2">
                  <strong>Feedback</strong> - Otrzymano 2 nowe oceny
                </Typography>
              </MenuItem>
              <MenuItem onClick={handleNotificationMenuClose}>
                <Typography variant="body2">
                  <strong>Alert AI</strong> - Wykryto wysokie ryzyko utraty klienta
                </Typography>
              </MenuItem>
            </Menu>

            {/* Avatar użytkownika */}
            <Tooltip title="Konto użytkownika">
              <IconButton
                size="large"
                edge="end"
                onClick={handleProfileMenuOpen}
                color="inherit"
              >
                <Avatar sx={{ width: 32, height: 32, bgcolor: 'secondary.main' }}>
                  U
                </Avatar>
              </IconButton>
            </Tooltip>

            {/* Menu użytkownika */}
            <Menu
              anchorEl={anchorEl}
              open={Boolean(anchorEl)}
              onClose={handleProfileMenuClose}
              transformOrigin={{ horizontal: 'right', vertical: 'top' }}
              anchorOrigin={{ horizontal: 'right', vertical: 'bottom' }}
            >
              <Box sx={{ px: 2, py: 1 }}>
                <Typography variant="subtitle1" sx={{ fontWeight: 600 }}>
                  Użytkownik
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  user@example.com
                </Typography>
              </Box>
              <Divider />
              <MenuItem onClick={handleProfileMenuClose}>
                <ListItemIcon>
                  <AccountCircleIcon fontSize="small" />
                </ListItemIcon>
                Mój profil
              </MenuItem>
              <MenuItem onClick={handleProfileMenuClose}>
                <ListItemIcon>
                  <SettingsIcon fontSize="small" />
                </ListItemIcon>
                Ustawienia
              </MenuItem>
              <Divider />
              <MenuItem onClick={handleProfileMenuClose}>
                Wyloguj
              </MenuItem>
            </Menu>
          </Box>
        </Toolbar>
      </AppBar>

      {/* Szuflada nawigacyjna */}
      <Box
        component="nav"
        sx={{ width: { md: drawerWidth }, flexShrink: { md: 0 } }}
      >
        {/* Mobile drawer */}
        <Drawer
          variant="temporary"
          open={mobileOpen}
          onClose={handleDrawerToggle}
          ModalProps={{
            keepMounted: true, // Lepsza wydajność na mobile
          }}
          sx={{
            display: { xs: 'block', md: 'none' },
            '& .MuiDrawer-paper': {
              boxSizing: 'border-box',
              width: drawerWidth,
            },
          }}
        >
          {drawerContent}
        </Drawer>

        {/* Desktop drawer */}
        <Drawer
          variant="permanent"
          sx={{
            display: { xs: 'none', md: 'block' },
            '& .MuiDrawer-paper': {
              boxSizing: 'border-box',
              width: drawerWidth,
              borderRight: '1px solid',
              borderColor: 'divider',
            },
          }}
          open
        >
          {drawerContent}
        </Drawer>
      </Box>

      {/* Główna zawartość */}
      <Box
        component="main"
        sx={{
          flexGrow: 1,
          p: 3,
          width: { md: `calc(100% - ${drawerWidth}px)` },
          minHeight: '100vh',
          backgroundColor: 'background.default',
        }}
      >
        {/* Odstęp dla AppBar */}
        <Toolbar />
        
        {/* Kontener na treść */}
        <Container maxWidth="xl" sx={{ mt: 2, mb: 4 }}>
          {children}
        </Container>
      </Box>
    </Box>
  );
};

export default MainLayout;
