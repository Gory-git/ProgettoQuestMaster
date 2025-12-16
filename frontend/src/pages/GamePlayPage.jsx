import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Container,
  Typography,
  Box,
  Paper,
  Button,
  Card,
  CardContent,
  CardMedia,
  CircularProgress,
  Alert,
  Grid
} from '@mui/material';
import { ArrowBack, Home } from '@mui/icons-material';
import { gameAPI } from '../services/api';

function GamePlayPage() {
  const { sessionId } = useParams();
  const navigate = useNavigate();
  const [session, setSession] = useState(null);
  const [narrative, setNarrative] = useState('');
  const [imageUrl, setImageUrl] = useState(null);
  const [actions, setActions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState(false);
  const [error, setError] = useState(null);
  const [isCompleted, setIsCompleted] = useState(false);

  useEffect(() => {
    loadSession();
  }, [sessionId]);

  const loadSession = async () => {
    try {
      const response = await gameAPI.getSession(sessionId);
      setSession(response.data.session);
      
      // Get available actions from response
      if (response.data.available_actions) {
        setActions(response.data.available_actions);
      }
      
      // Get the latest narrative from history
      const history = response.data.session.narrative_history;
      if (history && history.length > 0) {
        const latest = history[history.length - 1];
        setNarrative(latest.narrative);
        if (latest.image_url) {
          setImageUrl(latest.image_url);
        }
      }
      
      setIsCompleted(response.data.session.is_completed);
      setLoading(false);
    } catch (err) {
      setError('Failed to load game session: ' + err.message);
      setLoading(false);
    }
  };

  const handleAction = async (actionData) => {
    setActionLoading(true);
    setError(null);

    try {
      const response = await gameAPI.takeAction(sessionId, actionData.action, actionData.bindings || {});
      
      setSession(response.data.session);
      setNarrative(response.data.narrative);
      setImageUrl(response.data.image_url);
      setActions(response.data.available_actions);
      setIsCompleted(response.data.is_completed);
    } catch (err) {
      setError('Failed to take action: ' + err.message);
    } finally {
      setActionLoading(false);
    }
  };

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
        <CircularProgress />
      </Box>
    );
  }

  if (!session) {
    return <Alert severity="error">Game session not found</Alert>;
  }

  return (
    <Container maxWidth="md">
      <Box sx={{ mb: 3 }}>
        <Button 
          startIcon={<ArrowBack />} 
          onClick={() => navigate(`/stories/${session.story_id}`)}
        >
          Back to Story
        </Button>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      <Paper sx={{ p: 3, mb: 3 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
          <Typography variant="h5">
            Step {session.steps_taken}
          </Typography>
          {isCompleted && (
            <Typography variant="h6" color="success.main">
              Quest Completed! 🎉
            </Typography>
          )}
        </Box>

        {imageUrl && (
          <CardMedia
            component="img"
            height="300"
            image={imageUrl}
            alt="Scene illustration"
            sx={{ mb: 3, borderRadius: 2 }}
          />
        )}

        <Typography 
          variant="body1" 
          paragraph
          sx={{ 
            fontSize: '1.1rem',
            lineHeight: 1.8,
            whiteSpace: 'pre-wrap'
          }}
        >
          {narrative}
        </Typography>
      </Paper>

      {!isCompleted && (
        <Box>
          <Typography variant="h6" gutterBottom>
            What do you do?
          </Typography>
          
          <Grid container spacing={2}>
            {actions.map((action) => (
              <Grid item xs={12} key={action.id}>
                <Card 
                  sx={{ 
                    cursor: 'pointer',
                    transition: 'all 0.2s',
                    '&:hover': {
                      transform: 'translateY(-4px)',
                      boxShadow: 4
                    }
                  }}
                  onClick={() => !actionLoading && handleAction(action)}
                >
                  <CardContent>
                    <Typography variant="h6" gutterBottom>
                      {action.display_text}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      {action.description}
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>

          {actionLoading && (
            <Box sx={{ display: 'flex', justifyContent: 'center', mt: 3 }}>
              <CircularProgress />
              <Typography sx={{ ml: 2 }}>Processing your choice...</Typography>
            </Box>
          )}
        </Box>
      )}

      {isCompleted && (
        <Box sx={{ textAlign: 'center', mt: 4 }}>
          <Button
            variant="contained"
            size="large"
            startIcon={<Home />}
            onClick={() => navigate('/')}
          >
            Return to Home
          </Button>
        </Box>
      )}
    </Container>
  );
}

export default GamePlayPage;
