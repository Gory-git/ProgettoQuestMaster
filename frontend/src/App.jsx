import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import { 
  AppBar, 
  Toolbar, 
  Typography, 
  Container, 
  Box,
  Button 
} from '@mui/material';
import { AutoStories, Gamepad } from '@mui/icons-material';

// Pages
import HomePage from './pages/HomePage';
import StoryListPage from './pages/StoryListPage';
import StoryCreationPage from './pages/StoryCreationPage';
import StoryDetailPage from './pages/StoryDetailPage';
import GamePlayPage from './pages/GamePlayPage';

function App() {
  return (
    <Router>
      <Box sx={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
        <AppBar position="static">
          <Toolbar>
            <AutoStories sx={{ mr: 2 }} />
            <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
              QuestMaster
            </Typography>
            <Button color="inherit" component={Link} to="/">
              Home
            </Button>
            <Button color="inherit" component={Link} to="/stories">
              Stories
            </Button>
            <Button color="inherit" component={Link} to="/create">
              Create Story
            </Button>
          </Toolbar>
        </AppBar>
        
        <Container component="main" sx={{ mt: 4, mb: 4, flex: 1 }}>
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/stories" element={<StoryListPage />} />
            <Route path="/create" element={<StoryCreationPage />} />
            <Route path="/stories/:id" element={<StoryDetailPage />} />
            <Route path="/play/:sessionId" element={<GamePlayPage />} />
          </Routes>
        </Container>
        
        <Box 
          component="footer" 
          sx={{ 
            py: 3, 
            px: 2, 
            mt: 'auto',
            backgroundColor: (theme) => theme.palette.grey[200]
          }}
        >
          <Container maxWidth="sm">
            <Typography variant="body2" color="text.secondary" align="center">
              QuestMaster - Interactive Story Generation System
            </Typography>
          </Container>
        </Box>
      </Box>
    </Router>
  );
}

export default App;
