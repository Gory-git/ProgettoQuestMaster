import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Container,
  Typography,
  TextField,
  Button,
  Box,
  Paper,
  Grid,
  Alert,
  CircularProgress
} from '@mui/material';
import { Save } from '@mui/icons-material';
import { storyAPI } from '../services/api';

function StoryCreationPage() {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    lore_content: '',
    branching_factor_min: 2,
    branching_factor_max: 4,
    depth_min: 3,
    depth_max: 10
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: name.includes('factor') || name.includes('depth') ? 
        parseInt(value) || 0 : value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const response = await storyAPI.createStory(formData);
      const storyId = response.data.id;
      
      // Navigate to story detail page
      navigate(`/stories/${storyId}`);
    } catch (err) {
      setError('Failed to create story: ' + err.message);
      setLoading(false);
    }
  };

  return (
    <Container maxWidth="md">
      <Box sx={{ mb: 4 }}>
        <Typography variant="h3" component="h1" gutterBottom>
          Create New Story
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Enter your story lore and constraints to generate an interactive PDDL-based adventure
        </Typography>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      <Paper sx={{ p: 4 }}>
        <form onSubmit={handleSubmit}>
          <Grid container spacing={3}>
            <Grid item xs={12}>
              <TextField
                fullWidth
                required
                label="Story Title"
                name="title"
                value={formData.title}
                onChange={handleChange}
                placeholder="The Legend of the Crystal Cave"
              />
            </Grid>

            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Short Description"
                name="description"
                value={formData.description}
                onChange={handleChange}
                multiline
                rows={2}
                placeholder="A brief summary of your story..."
              />
            </Grid>

            <Grid item xs={12}>
              <TextField
                fullWidth
                required
                label="Lore Content"
                name="lore_content"
                value={formData.lore_content}
                onChange={handleChange}
                multiline
                rows={10}
                placeholder={`Describe your story world, including:
- Initial state: Where does the story begin? What's the situation?
- Goal: What must the protagonist achieve?
- Obstacles: What challenges stand in the way?
- Characters, locations, items
- Themes and atmosphere

Example:
You are a brave adventurer seeking the legendary Crystal of Power hidden deep within the Mystic Cave. The crystal is guarded by ancient puzzles and mystical creatures. You must navigate through dark tunnels, solve riddles, and make crucial decisions to reach your goal. Along the way, you'll encounter a wise old hermit who may help you, treacherous paths that could lead to danger, and magical artifacts that could aid your quest.`}
              />
            </Grid>

            <Grid item xs={12}>
              <Typography variant="h6" gutterBottom>
                Story Constraints
              </Typography>
            </Grid>

            <Grid item xs={6}>
              <TextField
                fullWidth
                required
                type="number"
                label="Min Branching Factor"
                name="branching_factor_min"
                value={formData.branching_factor_min}
                onChange={handleChange}
                inputProps={{ min: 1, max: 10 }}
                helperText="Minimum actions per step"
              />
            </Grid>

            <Grid item xs={6}>
              <TextField
                fullWidth
                required
                type="number"
                label="Max Branching Factor"
                name="branching_factor_max"
                value={formData.branching_factor_max}
                onChange={handleChange}
                inputProps={{ min: 1, max: 10 }}
                helperText="Maximum actions per step"
              />
            </Grid>

            <Grid item xs={6}>
              <TextField
                fullWidth
                required
                type="number"
                label="Min Depth"
                name="depth_min"
                value={formData.depth_min}
                onChange={handleChange}
                inputProps={{ min: 1, max: 100 }}
                helperText="Minimum steps to goal"
              />
            </Grid>

            <Grid item xs={6}>
              <TextField
                fullWidth
                required
                type="number"
                label="Max Depth"
                name="depth_max"
                value={formData.depth_max}
                onChange={handleChange}
                inputProps={{ min: 1, max: 100 }}
                helperText="Maximum steps to goal"
              />
            </Grid>

            <Grid item xs={12}>
              <Box sx={{ display: 'flex', gap: 2, justifyContent: 'flex-end' }}>
                <Button
                  variant="outlined"
                  onClick={() => navigate('/stories')}
                  disabled={loading}
                >
                  Cancel
                </Button>
                <Button
                  type="submit"
                  variant="contained"
                  startIcon={loading ? <CircularProgress size={20} /> : <Save />}
                  disabled={loading}
                >
                  {loading ? 'Creating...' : 'Create Story'}
                </Button>
              </Box>
            </Grid>
          </Grid>
        </form>
      </Paper>
    </Container>
  );
}

export default StoryCreationPage;
