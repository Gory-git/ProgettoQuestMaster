import React from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Container,
  Typography,
  Grid,
  Card,
  CardContent,
  CardActions,
  Button,
  Box
} from '@mui/material';
import { AutoStories, Gamepad, Psychology } from '@mui/icons-material';

function HomePage() {
  const navigate = useNavigate();

  return (
    <Container maxWidth="lg">
      <Box sx={{ textAlign: 'center', mb: 6 }}>
        <Typography variant="h2" component="h1" gutterBottom>
          Welcome to QuestMaster
        </Typography>
        <Typography variant="h5" color="text.secondary" paragraph>
          Create Interactive Stories with AI-Powered PDDL Planning
        </Typography>
      </Box>

      <Grid container spacing={4}>
        <Grid item xs={12} md={4}>
          <Card sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
            <CardContent sx={{ flexGrow: 1 }}>
              <AutoStories sx={{ fontSize: 60, color: 'primary.main', mb: 2 }} />
              <Typography gutterBottom variant="h5" component="h2">
                Phase 1: Story Creation
              </Typography>
              <Typography>
                Create logically consistent quest narratives using PDDL and LLM.
                Get assistance from our Reflection Agent to refine your stories.
              </Typography>
            </CardContent>
            <CardActions>
              <Button 
                size="large" 
                onClick={() => navigate('/create')}
                fullWidth
                variant="contained"
              >
                Create Story
              </Button>
            </CardActions>
          </Card>
        </Grid>

        <Grid item xs={12} md={4}>
          <Card sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
            <CardContent sx={{ flexGrow: 1 }}>
              <Gamepad sx={{ fontSize: 60, color: 'secondary.main', mb: 2 }} />
              <Typography gutterBottom variant="h5" component="h2">
                Phase 2: Play Stories
              </Typography>
              <Typography>
                Experience interactive narratives with dynamic choices.
                Each decision shapes your unique adventure through the story world.
              </Typography>
            </CardContent>
            <CardActions>
              <Button 
                size="large" 
                onClick={() => navigate('/stories')}
                fullWidth
                variant="contained"
              >
                Browse Stories
              </Button>
            </CardActions>
          </Card>
        </Grid>

        <Grid item xs={12} md={4}>
          <Card sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
            <CardContent sx={{ flexGrow: 1 }}>
              <Psychology sx={{ fontSize: 60, color: 'success.main', mb: 2 }} />
              <Typography gutterBottom variant="h5" component="h2">
                AI-Powered Refinement
              </Typography>
              <Typography>
                Our Reflection Agent analyzes your PDDL and provides intelligent
                feedback to help you create compelling, consistent narratives.
              </Typography>
            </CardContent>
            <CardActions>
              <Button 
                size="large" 
                onClick={() => navigate('/stories')}
                fullWidth
                variant="outlined"
              >
                Learn More
              </Button>
            </CardActions>
          </Card>
        </Grid>
      </Grid>

      <Box sx={{ mt: 8, p: 4, bgcolor: 'background.paper', borderRadius: 2 }}>
        <Typography variant="h4" gutterBottom>
          Features
        </Typography>
        <Grid container spacing={2}>
          <Grid item xs={12} sm={6}>
            <Typography variant="body1" paragraph>
              ✅ Dynamic decision-making at every step
            </Typography>
            <Typography variant="body1" paragraph>
              ✅ Real-time PDDL validation
            </Typography>
            <Typography variant="body1" paragraph>
              ✅ Interactive chat with Reflection Agent
            </Typography>
          </Grid>
          <Grid item xs={12} sm={6}>
            <Typography variant="body1" paragraph>
              ✅ Narrative image generation with DALL-E
            </Typography>
            <Typography variant="body1" paragraph>
              ✅ Story persistence and management
            </Typography>
            <Typography variant="body1" paragraph>
              ✅ Branching factor and depth control
            </Typography>
          </Grid>
        </Grid>
      </Box>
    </Container>
  );
}

export default HomePage;
