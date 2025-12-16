import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Container,
  Typography,
  Grid,
  Card,
  CardContent,
  CardActions,
  Button,
  Chip,
  Box,
  CircularProgress,
  Alert
} from '@mui/material';
import { CheckCircle, PlayArrow, Edit } from '@mui/icons-material';
import { storyAPI, gameAPI } from '../services/api';

function StoryListPage() {
  const navigate = useNavigate();
  const [stories, setStories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadStories();
  }, []);

  const loadStories = async () => {
    try {
      const response = await storyAPI.getStories();
      setStories(response.data.stories);
      setLoading(false);
    } catch (err) {
      setError('Failed to load stories: ' + err.message);
      setLoading(false);
    }
  };

  const handlePlay = async (storyId) => {
    try {
      const response = await gameAPI.createSession(storyId);
      navigate(`/play/${response.data.session.id}`);
    } catch (err) {
      setError('Failed to start game: ' + err.message);
    }
  };

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Container maxWidth="lg">
      <Box sx={{ mb: 4 }}>
        <Typography variant="h3" component="h1" gutterBottom>
          Story Library
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Browse and play interactive stories, or continue editing your drafts
        </Typography>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {stories.length === 0 ? (
        <Box sx={{ textAlign: 'center', py: 8 }}>
          <Typography variant="h5" color="text.secondary" gutterBottom>
            No stories yet
          </Typography>
          <Button 
            variant="contained" 
            size="large"
            onClick={() => navigate('/create')}
            sx={{ mt: 2 }}
          >
            Create Your First Story
          </Button>
        </Box>
      ) : (
        <Grid container spacing={3}>
          {stories.map((story) => (
            <Grid item xs={12} md={6} lg={4} key={story.id}>
              <Card sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
                <CardContent sx={{ flexGrow: 1 }}>
                  <Box sx={{ mb: 2 }}>
                    <Chip 
                      label={story.status}
                      color={
                        story.status === 'validated' ? 'success' :
                        story.status === 'generated' ? 'info' : 'default'
                      }
                      size="small"
                      icon={story.is_validated ? <CheckCircle /> : null}
                    />
                  </Box>
                  <Typography gutterBottom variant="h5" component="h2">
                    {story.title}
                  </Typography>
                  <Typography variant="body2" color="text.secondary" paragraph>
                    {story.description || 'No description'}
                  </Typography>
                  <Typography variant="caption" display="block" sx={{ mt: 2 }}>
                    Depth: {story.depth_min}-{story.depth_max} steps
                  </Typography>
                  <Typography variant="caption" display="block">
                    Branching: {story.branching_factor_min}-{story.branching_factor_max} actions
                  </Typography>
                </CardContent>
                <CardActions>
                  <Button 
                    size="small" 
                    startIcon={<Edit />}
                    onClick={() => navigate(`/stories/${story.id}`)}
                  >
                    Edit
                  </Button>
                  {story.is_validated && (
                    <Button 
                      size="small" 
                      color="primary"
                      startIcon={<PlayArrow />}
                      onClick={() => handlePlay(story.id)}
                    >
                      Play
                    </Button>
                  )}
                </CardActions>
              </Card>
            </Grid>
          ))}
        </Grid>
      )}
    </Container>
  );
}

export default StoryListPage;
