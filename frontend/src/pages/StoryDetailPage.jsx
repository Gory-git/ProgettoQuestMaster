import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Container,
  Typography,
  Box,
  Paper,
  Button,
  Tabs,
  Tab,
  Alert,
  CircularProgress,
  Chip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  List,
  ListItem,
  ListItemText
} from '@mui/material';
import { 
  Code, 
  PlayArrow, 
  CheckCircle, 
  Error,
  Psychology,
  Refresh
} from '@mui/icons-material';
import { storyAPI, gameAPI } from '../services/api';

function StoryDetailPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [story, setStory] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState(0);
  const [generating, setGenerating] = useState(false);
  const [validating, setValidating] = useState(false);
  const [validationResult, setValidationResult] = useState(null);
  const [chatOpen, setChatOpen] = useState(false);
  const [chatHistory, setChatHistory] = useState([]);
  const [chatMessage, setChatMessage] = useState('');

  useEffect(() => {
    loadStory();
  }, [id]);

  const loadStory = async () => {
    try {
      const response = await storyAPI.getStory(id);
      setStory(response.data);
      setLoading(false);
    } catch (err) {
      setError('Failed to load story: ' + err.message);
      setLoading(false);
    }
  };

  const handleGeneratePDDL = async () => {
    setGenerating(true);
    setError(null);
    try {
      const response = await storyAPI.generatePDDL(id);
      setStory(response.data.story);
      setActiveTab(1); // Switch to PDDL tab
    } catch (err) {
      setError('Failed to generate PDDL: ' + err.message);
    } finally {
      setGenerating(false);
    }
  };

  const handleValidate = async () => {
    setValidating(true);
    setError(null);
    try {
      const response = await storyAPI.validatePDDL(id);
      setValidationResult(response.data);
      if (response.data.valid) {
        setStory(prev => ({ ...prev, is_validated: true, status: 'validated' }));
      }
    } catch (err) {
      setError('Failed to validate PDDL: ' + err.message);
    } finally {
      setValidating(false);
    }
  };

  const handleRefine = async () => {
    if (!validationResult || !validationResult.refinement_id) return;
    
    try {
      const response = await storyAPI.refinePDDL(id, {
        refinement_id: validationResult.refinement_id,
        author_input: 'Please fix the identified issues'
      });
      setStory(response.data.story);
      setValidationResult(null);
      setActiveTab(1); // Show updated PDDL
    } catch (err) {
      setError('Failed to refine PDDL: ' + err.message);
    }
  };

  const handleSendMessage = async () => {
    if (!chatMessage.trim()) return;

    const newHistory = [...chatHistory, { role: 'user', content: chatMessage }];
    setChatHistory(newHistory);
    setChatMessage('');

    try {
      const response = await storyAPI.chatWithAgent(id, {
        conversation_history: newHistory,
        message: chatMessage
      });
      
      setChatHistory([
        ...newHistory,
        { role: 'assistant', content: response.data.response }
      ]);
    } catch (err) {
      setError('Chat error: ' + err.message);
    }
  };

  const handlePlay = async () => {
    try {
      const response = await gameAPI.createSession(id);
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

  if (!story) {
    return <Alert severity="error">Story not found</Alert>;
  }

  return (
    <Container maxWidth="lg">
      <Box sx={{ mb: 4 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
          <Typography variant="h3" component="h1">
            {story.title}
          </Typography>
          <Box sx={{ display: 'flex', gap: 1 }}>
            <Chip 
              label={story.status}
              color={story.status === 'validated' ? 'success' : 'default'}
              icon={story.is_validated ? <CheckCircle /> : null}
            />
          </Box>
        </Box>
        <Typography variant="body1" color="text.secondary">
          {story.description}
        </Typography>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      <Box sx={{ mb: 3, display: 'flex', gap: 2 }}>
        {!story.pddl_domain && (
          <Button
            variant="contained"
            onClick={handleGeneratePDDL}
            disabled={generating}
            startIcon={generating ? <CircularProgress size={20} /> : <Code />}
          >
            {generating ? 'Generating...' : 'Generate PDDL'}
          </Button>
        )}
        {story.pddl_domain && !story.is_validated && (
          <>
            <Button
              variant="contained"
              onClick={handleValidate}
              disabled={validating}
              startIcon={validating ? <CircularProgress size={20} /> : <CheckCircle />}
            >
              {validating ? 'Validating...' : 'Validate PDDL'}
            </Button>
            <Button
              variant="outlined"
              onClick={handleGeneratePDDL}
              disabled={generating}
              startIcon={<Refresh />}
            >
              Regenerate
            </Button>
          </>
        )}
        {story.is_validated && (
          <Button
            variant="contained"
            color="success"
            onClick={handlePlay}
            startIcon={<PlayArrow />}
          >
            Play Story
          </Button>
        )}
        <Button
          variant="outlined"
          onClick={() => setChatOpen(true)}
          startIcon={<Psychology />}
        >
          Chat with Agent
        </Button>
      </Box>

      {validationResult && !validationResult.valid && (
        <Alert 
          severity="warning" 
          sx={{ mb: 3 }}
          action={
            <Button color="inherit" size="small" onClick={handleRefine}>
              Auto-Fix
            </Button>
          }
        >
          <Typography variant="subtitle2">Validation Errors:</Typography>
          <List dense>
            {validationResult.errors.map((error, idx) => (
              <ListItem key={idx}>
                <ListItemText primary={error} />
              </ListItem>
            ))}
          </List>
          {validationResult.reflection && (
            <Box sx={{ mt: 2, p: 2, bgcolor: 'background.paper', borderRadius: 1 }}>
              <Typography variant="subtitle2">Reflection Agent Analysis:</Typography>
              <Typography variant="body2" sx={{ whiteSpace: 'pre-wrap', mt: 1 }}>
                {validationResult.reflection.analysis}
              </Typography>
            </Box>
          )}
        </Alert>
      )}

      {validationResult && validationResult.valid && (
        <Alert severity="success" sx={{ mb: 3 }}>
          ✅ PDDL validated successfully! Your story is ready to play.
        </Alert>
      )}

      <Paper>
        <Tabs value={activeTab} onChange={(e, v) => setActiveTab(v)}>
          <Tab label="Lore" />
          <Tab label="PDDL Domain" disabled={!story.pddl_domain} />
          <Tab label="PDDL Problem" disabled={!story.pddl_problem} />
        </Tabs>
        
        <Box sx={{ p: 3 }}>
          {activeTab === 0 && (
            <Box>
              <Typography variant="h6" gutterBottom>Story Lore</Typography>
              <Typography 
                component="pre" 
                sx={{ 
                  whiteSpace: 'pre-wrap', 
                  fontFamily: 'monospace',
                  bgcolor: 'grey.100',
                  p: 2,
                  borderRadius: 1
                }}
              >
                {story.lore_content}
              </Typography>
            </Box>
          )}
          {activeTab === 1 && story.pddl_domain && (
            <Box>
              <Typography variant="h6" gutterBottom>PDDL Domain</Typography>
              <Typography 
                component="pre" 
                sx={{ 
                  whiteSpace: 'pre-wrap', 
                  fontFamily: 'monospace',
                  bgcolor: 'grey.100',
                  p: 2,
                  borderRadius: 1,
                  overflow: 'auto'
                }}
              >
                {story.pddl_domain}
              </Typography>
            </Box>
          )}
          {activeTab === 2 && story.pddl_problem && (
            <Box>
              <Typography variant="h6" gutterBottom>PDDL Problem</Typography>
              <Typography 
                component="pre" 
                sx={{ 
                  whiteSpace: 'pre-wrap', 
                  fontFamily: 'monospace',
                  bgcolor: 'grey.100',
                  p: 2,
                  borderRadius: 1,
                  overflow: 'auto'
                }}
              >
                {story.pddl_problem}
              </Typography>
            </Box>
          )}
        </Box>
      </Paper>

      {/* Chat Dialog */}
      <Dialog open={chatOpen} onClose={() => setChatOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>Chat with Reflection Agent</DialogTitle>
        <DialogContent>
          <Box sx={{ mb: 2, minHeight: 300, maxHeight: 400, overflow: 'auto' }}>
            {chatHistory.length === 0 ? (
              <Typography color="text.secondary" align="center" sx={{ mt: 4 }}>
                Start a conversation with the Reflection Agent to get help with your story.
              </Typography>
            ) : (
              chatHistory.map((msg, idx) => (
                <Paper 
                  key={idx} 
                  sx={{ 
                    p: 2, 
                    mb: 1,
                    bgcolor: msg.role === 'user' ? 'primary.light' : 'grey.100'
                  }}
                >
                  <Typography variant="caption" display="block">
                    {msg.role === 'user' ? 'You' : 'Agent'}
                  </Typography>
                  <Typography variant="body2">{msg.content}</Typography>
                </Paper>
              ))
            )}
          </Box>
          <TextField
            fullWidth
            multiline
            rows={3}
            value={chatMessage}
            onChange={(e) => setChatMessage(e.target.value)}
            placeholder="Ask the Reflection Agent for help..."
            onKeyPress={(e) => {
              if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                handleSendMessage();
              }
            }}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setChatOpen(false)}>Close</Button>
          <Button onClick={handleSendMessage} variant="contained">Send</Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
}

export default StoryDetailPage;
