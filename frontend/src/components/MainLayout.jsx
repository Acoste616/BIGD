/**
 * Główny layout aplikacji
 * Zawiera nawigację, strukturę strony i kontener na treść
 */
import React, { useState } from 'react';
import { Link, useLocation, Outlet } from 'react-router-dom';
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

const MainLayout = () => {
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

  // Menu powiadomień
  const handleNotificationMenuOpen = (event) => {
    setNotificationAnchor(event.currentTarget);
  };

  const handleNotificationMenuClose = () => {
    setNotificationAnchor(null);
  };

  // Sprawdzanie czy ścieżka jest aktywna
  const isActivePath = (path) => {
    if (path === '/') {
      return location.pathname === '/';
    }
    return location.pathname.startsWith(path);
  };

  // Renderowanie elementu menu z badge
  const renderMenuItem = (item) => (
    <ListItem key={item.text} disablePadding>
      <ListItemButton
        component={Link}
        to={item.path}
        selected={isActivePath(item.path)}
        sx={{
          '&.Mui-selected': {
            backgroundColor: 'primary.main',
            color: 'primary.contrastText',
            '&:hover': {
              backgroundColor: 'primary.dark',
            },
          },
        }}
      >
        <ListItemIcon
          sx={{
            color: isActivePath(item.path) ? 'primary.contrastText' : 'inherit',
          }}
        >
          {item.icon}
        </ListItemIcon>
        <ListItemText primary={item.text} />
        {item.badge && (
          <Badge
            badgeContent={item.badge.content}
            color={item.badge.color}
            sx={{ ml: 1 }}
          />
        )}
      </ListItemButton>
    </ListItem>
  );

  // Zawartość szuflady
  const drawerContent = (
    <Box>
      <Box
        sx={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          p: 2,
          minHeight: 64,
          borderBottom: 1,
          borderColor: 'divider',
        }}
      >
        <Box sx={{ textAlign: 'center' }}>
          <Typography variant="h6" sx={{ fontWeight: 700, lineHeight: 1.2 }}>
            Sales Co-Pilot
          </Typography>
          <Typography variant="caption" sx={{ color: 'text.secondary' }}>
            AI Assistant v0.2
          </Typography>
        </Box>
      </Box>
      <List>
        {menuItems.map(renderMenuItem)}
      </List>
    </Box>
  );

  return (
    <Box sx={{ display: 'flex', minHeight: '100vh' }}>
      {/* AppBar */}
      <AppBar
        position="fixed"
        sx={{
          width: { sm: `calc(100% - ${drawerWidth}px)` },
          ml: { sm: `${drawerWidth}px` },
          zIndex: theme.zIndex.drawer + 1,
        }}
      >
        <Toolbar>
          <IconButton
            color="inherit"
            aria-label="open drawer"
            edge="start"
            onClick={handleDrawerToggle}
            sx={{ mr: 2, display: { sm: 'none' } }}
          >
            <MenuIcon />
          </IconButton>
          
          <Typography variant="h6" noWrap component="div" sx={{ flexGrow: 1 }}>
            {menuItems.find(item => isActivePath(item.path))?.text || 'Sales Co-Pilot'}
          </Typography>

          {/* Powiadomienia */}
          <Tooltip title="Powiadomienia">
            <IconButton
              color="inherit"
              onClick={handleNotificationMenuOpen}
              sx={{ mr: 1 }}
            >
              <Badge badgeContent={3} color="error">
                <NotificationsIcon />
              </Badge>
            </IconButton>
          </Tooltip>

          {/* Menu użytkownika */}
          <Tooltip title="Konto użytkownika">
            <IconButton
              color="inherit"
              onClick={handleProfileMenuOpen}
            >
              <Avatar sx={{ width: 32, height: 32 }}>
                <AccountCircleIcon />
              </Avatar>
            </IconButton>
          </Tooltip>
        </Toolbar>
      </AppBar>

      {/* Szuflada nawigacyjna */}
      <Box
        component="nav"
        sx={{ width: { sm: drawerWidth }, flexShrink: { sm: 0 } }}
      >
        {/* Mobilna szuflada */}
        <Drawer
          variant="temporary"
          open={mobileOpen}
          onClose={handleDrawerToggle}
          ModalProps={{
            keepMounted: true, // Lepsze wydajność na urządzeniach mobilnych
          }}
          sx={{
            display: { xs: 'block', sm: 'none' },
            '& .MuiDrawer-paper': { boxSizing: 'border-box', width: drawerWidth },
          }}
        >
          {drawerContent}
        </Drawer>

        {/* Desktop szuflada */}
        <Drawer
          variant="permanent"
          sx={{
            display: { xs: 'none', sm: 'block' },
            '& .MuiDrawer-paper': { boxSizing: 'border-box', width: drawerWidth },
          }}
          open
        >
          {drawerContent}
        </Drawer>
      </Box>

      {/* Główna treść */}
      <Box
        component="main"
        sx={{
          flexGrow: 1,
          p: 3,
          width: { sm: `calc(100% - ${drawerWidth}px)` },
          mt: 8, // Odstęp od AppBar
        }}
      >
        <Outlet />
      </Box>

      {/* Menu powiadomień */}
      <Menu
        anchorEl={notificationAnchor}
        open={Boolean(notificationAnchor)}
        onClose={handleNotificationMenuClose}
        anchorOrigin={{
          vertical: 'bottom',
          horizontal: 'right',
        }}
        transformOrigin={{
          vertical: 'top',
          horizontal: 'right',
        }}
      >
        <MenuItem onClick={handleNotificationMenuClose}>
          Nowy klient dodany
        </MenuItem>
        <MenuItem onClick={handleNotificationMenuClose}>
          Sesja zakończona
        </MenuItem>
        <MenuItem onClick={handleNotificationMenuClose}>
          Aktualizacja systemu
        </MenuItem>
      </Menu>

      {/* Menu użytkownika */}
      <Menu
        anchorEl={anchorEl}
        open={Boolean(anchorEl)}
        onClose={handleProfileMenuClose}
        anchorOrigin={{
          vertical: 'bottom',
          horizontal: 'right',
        }}
        transformOrigin={{
          vertical: 'top',
          horizontal: 'right',
        }}
      >
        <MenuItem onClick={handleProfileMenuClose}>
          <AccountCircleIcon sx={{ mr: 1 }} />
          Profil
        </MenuItem>
        <MenuItem onClick={handleProfileMenuClose}>
          <SettingsIcon sx={{ mr: 1 }} />
          Ustawienia
        </MenuItem>
        <Divider />
        <MenuItem onClick={handleProfileMenuClose}>
          Wyloguj
        </MenuItem>
      </Menu>
    </Box>
  );
};

export default MainLayout;
