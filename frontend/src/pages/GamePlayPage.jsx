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
  const [questSummary, setQuestSummary] = useState(null);

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
      // If session is already completed, the last narrative_history entry is the summary
      if (response.data.session.is_completed) {
        const hist = response.data.session.narrative_history;
        if (hist && hist.length > 0) {
          setQuestSummary(hist[hist.length - 1].narrative);
        }
      }
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
      if (response.data.quest_summary) {
        setQuestSummary(response.data.quest_summary);
      }
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

      {isCompleted ? (
        /* ─────────────── VICTORY SCREEN ─────────────── */
        <Box>
          {/* Hero banner */}
          <Paper
            elevation={6}
            sx={{
              p: 4,
              mb: 3,
              background: 'linear-gradient(135deg, #1a237e 0%, #4a148c 50%, #880e4f 100%)',
              color: 'white',
              textAlign: 'center',
              borderRadius: 3,
            }}
          >
            <Typography variant="h3" gutterBottom sx={{ fontWeight: 'bold' }}>
              🏆 Quest Complete!
            </Typography>
            <Typography variant="h5" sx={{ opacity: 0.9 }}>
              {session?.steps_taken} steps to victory
            </Typography>
          </Paper>

          {/* Quest summary */}
          <Paper elevation={3} sx={{ p: 4, mb: 3 }}>
            <Typography variant="h5" gutterBottom sx={{ fontWeight: 'bold', mb: 3 }}>
              📖 Your Adventure
            </Typography>

            {imageUrl && (
              <CardMedia
                component="img"
                height="280"
                image={imageUrl}
                alt="Final scene"
                sx={{ mb: 3, borderRadius: 2 }}
              />
            )}

            <Typography
              variant="body1"
              sx={{
                fontSize: '1.1rem',
                lineHeight: 1.9,
                whiteSpace: 'pre-wrap',
                fontStyle: 'italic',
              }}
            >
              {questSummary || narrative}
            </Typography>
          </Paper>

          {/* Steps timeline — list of actions taken */}
          {session?.action_history && session.action_history.length > 0 && (
            <Paper elevation={2} sx={{ p: 3, mb: 3 }}>
              <Typography variant="h6" gutterBottom sx={{ fontWeight: 'bold' }}>
                ⚔️ Steps Taken
              </Typography>
              <Box component="ol" sx={{ pl: 3, m: 0 }}>
                {session.action_history.map((entry, idx) => (
                  <Box
                    component="li"
                    key={idx}
                    sx={{ mb: 1, fontSize: '0.95rem', color: 'text.secondary' }}
                  >
                    <Typography variant="body2" component="span" sx={{ color: 'text.primary', fontWeight: 500 }}>
                      Step {entry.step}:
                    </Typography>{' '}
                    {entry.action.replace(/_/g, ' ')}
                    {entry.bindings && Object.keys(entry.bindings).length > 0 && (
                      <Typography variant="body2" component="span" sx={{ color: 'text.disabled' }}>
                        {' '}({Object.values(entry.bindings).join(', ')})
                      </Typography>
                    )}
                  </Box>
                ))}
              </Box>
            </Paper>
          )}

          {/* Navigation buttons */}
          <Box sx={{ display: 'flex', gap: 2, justifyContent: 'center', mt: 2 }}>
            <Button
              variant="outlined"
              startIcon={<ArrowBack />}
              onClick={() => navigate(`/stories/${session.story_id}`)}
              size="large"
            >
              Back to Story
            </Button>
            <Button
              variant="contained"
              startIcon={<Home />}
              onClick={() => navigate('/')}
              size="large"
              color="primary"
            >
              Home
            </Button>
          </Box>
        </Box>
      ) : (
        /* ─────────────── NORMAL GAME SCREEN ─────────────── */
        <Box>
          <Paper sx={{ p: 3, mb: 3 }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
              <Typography variant="h5">
                Step {session.steps_taken}
              </Typography>
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
        </Box>
      )}
    </Container>
  );
}

export default GamePlayPage;
