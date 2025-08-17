/**
 * StrategicPanel - Prawa strona interfejsu konwersacyjnego
 * 
 * Zawiera:
 * - Sekcję archetypów na górze (1-2 najbardziej prawdopodobne)
 * - Sekcję strategii poniżej (rozwijane panele z nuggetami wiedzy)
 */
import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Paper,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Chip,
  LinearProgress,
  Stack,
  Divider,
  Card,
  CardContent,
  Alert,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  IconButton,
  Tooltip,
  Badge
} from '@mui/material';
import {
  ExpandMore as ExpandMoreIcon,
  Psychology as PsychologyIcon,
  Lightbulb as LightbulbIcon,
  TrendingUp as TrendingUpIcon,
  Star as StarIcon,
  Info as InfoIcon,
  Refresh as RefreshIcon,
  QuestionAnswer as QuestionAnswerIcon,
  SupportAgent as SupportAgentIcon,
  Assessment as AssessmentIcon
} from '@mui/icons-material';
import { getKnowledgeList } from '../../services/knowledgeApi';

const StrategicPanel = ({ 
  archetypes = [], 
  insights = [], 
  currentSession, 
  isLoading 
}) => {
  const [knowledgeItems, setKnowledgeItems] = useState([]);
  const [loadingKnowledge, setLoadingKnowledge] = useState(false);
  const [expandedAccordion, setExpandedAccordion] = useState('archetypes');

  // Load strategic knowledge based on dominant archetype
  useEffect(() => {
    if (archetypes.length > 0) {
      loadStrategicKnowledge(archetypes[0]);
    }
  }, [archetypes]);

  const loadStrategicKnowledge = async (dominantArchetype) => {
    if (!dominantArchetype || !dominantArchetype.name) return;

    setLoadingKnowledge(true);
    try {
      // Fetch knowledge items relevant to the archetype
      const response = await getKnowledgeList({
        archetype: dominantArchetype.name,
        page: 1,
        size: 5
      });
      
      setKnowledgeItems(response.items || []);
    } catch (error) {
      console.error('Error loading strategic knowledge:', error);
    } finally {
      setLoadingKnowledge(false);
    }
  };

  const handleAccordionChange = (panel) => (event, isExpanded) => {
    setExpandedAccordion(isExpanded ? panel : false);
  };

  // Get archetype icon
  const getArchetypeIcon = (archetypeName) => {
    const iconMap = {
      'Zdobywca Statusu': '🏆',
      'Strażnik Rodziny': '👨‍👩‍👧‍👦',
      'Pragmatyczny Analityk': '📊',
      'Eko-Entuzjasta': '🌱',
      'Pionier Technologii': '🚀',
      'Techniczny Sceptyk': '🤔',
      'Lojalista Premium': '💎',
      'Łowca Okazji': '💰',
      'Niezdecydowany Odkrywca': '🧭',
      'Entuzjasta Osiągów': '⚡'
    };
    return iconMap[archetypeName] || '👤';
  };

  // Get confidence color
  const getConfidenceColor = (confidence) => {
    if (confidence >= 80) return 'success';
    if (confidence >= 60) return 'warning';
    return 'error';
  };

  return (
    <Box 
      sx={{ 
        height: '100%',
        display: 'flex',
        flexDirection: 'column',
        overflow: 'hidden'
      }}
    >
      {/* Header */}
      <Box 
        sx={{ 
          p: 2,
          bgcolor: 'grey.50',
          borderBottom: '1px solid',
          borderColor: 'divider',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center'
        }}
      >
        <Typography variant="h6" sx={{ fontWeight: 600, display: 'flex', alignItems: 'center', gap: 1 }}>
          <AssessmentIcon color="primary" />
          Strategic Panel
        </Typography>
        
        <Tooltip title="Refresh insights">
          <IconButton size="small" onClick={() => loadStrategicKnowledge(archetypes[0])}>
            <RefreshIcon />
          </IconButton>
        </Tooltip>
      </Box>

      {/* Content */}
      <Box sx={{ flexGrow: 1, overflow: 'auto', p: 1 }}>
        {/* Sekcja Archetypów */}
        <Accordion 
          expanded={expandedAccordion === 'archetypes'} 
          onChange={handleAccordionChange('archetypes')}
          sx={{ mb: 1 }}
        >
          <AccordionSummary expandIcon={<ExpandMoreIcon />}>
            <Typography variant="subtitle1" sx={{ fontWeight: 600, display: 'flex', alignItems: 'center', gap: 1 }}>
              <PsychologyIcon color="primary" fontSize="small" />
              Customer Archetypes
              {archetypes.length > 0 && (
                <Badge badgeContent={archetypes.length} color="primary" />
              )}
            </Typography>
          </AccordionSummary>
          <AccordionDetails>
            {archetypes.length === 0 ? (
              <Alert severity="info" sx={{ fontSize: '0.875rem' }}>
                Start a conversation to identify customer archetypes
              </Alert>
            ) : (
              <Stack spacing={2}>
                {archetypes.slice(0, 2).map((archetype, index) => (
                  <Card 
                    key={index}
                    variant="outlined" 
                    sx={{ 
                      position: 'relative',
                      bgcolor: index === 0 ? 'primary.lighter' : 'background.paper'
                    }}
                  >
                    <CardContent sx={{ p: 2, '&:last-child': { pb: 2 } }}>
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 1 }}>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                          <Typography variant="h6" component="span">
                            {getArchetypeIcon(archetype.name)}
                          </Typography>
                          <Typography variant="subtitle2" sx={{ fontWeight: 600 }}>
                            {archetype.name}
                          </Typography>
                          {index === 0 && (
                            <Chip 
                              label="Primary" 
                              size="small" 
                              color="primary" 
                              variant="outlined"
                            />
                          )}
                        </Box>
                        <Chip 
                          label={`${archetype.confidence || 0}%`}
                          size="small"
                          color={getConfidenceColor(archetype.confidence || 0)}
                        />
                      </Box>
                      
                      <LinearProgress 
                        variant="determinate" 
                        value={archetype.confidence || 0} 
                        sx={{ 
                          height: 6, 
                          borderRadius: 3,
                          mb: 1
                        }}
                        color={getConfidenceColor(archetype.confidence || 0)}
                      />
                      
                      {archetype.description && (
                        <Typography variant="body2" color="text.secondary" sx={{ fontSize: '0.8rem' }}>
                          {archetype.description}
                        </Typography>
                      )}
                    </CardContent>
                  </Card>
                ))}
              </Stack>
            )}
          </AccordionDetails>
        </Accordion>

        {/* Sekcja Strategic Insights */}
        <Accordion 
          expanded={expandedAccordion === 'insights'} 
          onChange={handleAccordionChange('insights')}
          sx={{ mb: 1 }}
        >
          <AccordionSummary expandIcon={<ExpandMoreIcon />}>
            <Typography variant="subtitle1" sx={{ fontWeight: 600, display: 'flex', alignItems: 'center', gap: 1 }}>
              <LightbulbIcon color="warning" fontSize="small" />
              Strategic Insights
              {insights.length > 0 && (
                <Badge badgeContent={insights.length} color="warning" />
              )}
            </Typography>
          </AccordionSummary>
          <AccordionDetails>
            {insights.length === 0 ? (
              <Alert severity="info" sx={{ fontSize: '0.875rem' }}>
                AI insights will appear here as you interact with customers
              </Alert>
            ) : (
              <List dense>
                {insights.slice(0, 5).map((insight, index) => (
                  <ListItem key={index} sx={{ px: 0 }}>
                    <ListItemIcon sx={{ minWidth: 32 }}>
                      <StarIcon color="warning" fontSize="small" />
                    </ListItemIcon>
                    <ListItemText 
                      primary={insight}
                      primaryTypographyProps={{ 
                        fontSize: '0.875rem',
                        fontWeight: 500
                      }}
                    />
                  </ListItem>
                ))}
              </List>
            )}
          </AccordionDetails>
        </Accordion>

        {/* Sekcja Knowledge Base */}
        <Accordion 
          expanded={expandedAccordion === 'knowledge'} 
          onChange={handleAccordionChange('knowledge')}
        >
          <AccordionSummary expandIcon={<ExpandMoreIcon />}>
            <Typography variant="subtitle1" sx={{ fontWeight: 600, display: 'flex', alignItems: 'center', gap: 1 }}>
              <SupportAgentIcon color="success" fontSize="small" />
              Knowledge Base
              {knowledgeItems.length > 0 && (
                <Badge badgeContent={knowledgeItems.length} color="success" />
              )}
            </Typography>
          </AccordionSummary>
          <AccordionDetails>
            {loadingKnowledge ? (
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, py: 2 }}>
                <LinearProgress sx={{ flexGrow: 1 }} />
                <Typography variant="caption" color="text.secondary">
                  Loading insights...
                </Typography>
              </Box>
            ) : knowledgeItems.length === 0 ? (
              <Alert severity="info" sx={{ fontSize: '0.875rem' }}>
                Relevant knowledge tips will appear here based on identified archetypes
              </Alert>
            ) : (
              <Stack spacing={1.5}>
                {knowledgeItems.map((item, index) => (
                  <Paper 
                    key={item.id || index}
                    variant="outlined"
                    sx={{ p: 2, bgcolor: 'success.lighter' }}
                  >
                    <Typography variant="subtitle2" sx={{ fontWeight: 600, mb: 0.5 }}>
                      💡 {item.title || 'Strategic Tip'}
                    </Typography>
                    <Typography variant="body2" sx={{ fontSize: '0.8rem', lineHeight: 1.4 }}>
                      {item.content || item.description || 'Knowledge content...'}
                    </Typography>
                    {item.knowledge_type && (
                      <Chip 
                        label={item.knowledge_type} 
                        size="small" 
                        variant="outlined"
                        sx={{ mt: 1, fontSize: '0.7rem', height: 20 }}
                      />
                    )}
                  </Paper>
                ))}
              </Stack>
            )}
          </AccordionDetails>
        </Accordion>

        {/* Status Footer */}
        <Box sx={{ mt: 2, p: 1, bgcolor: 'grey.50', borderRadius: 1 }}>
          <Typography variant="caption" color="text.secondary" sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
            <InfoIcon fontSize="small" />
            {currentSession ? `Session Active` : 'Waiting for session...'}
          </Typography>
        </Box>
      </Box>
    </Box>
  );
};

export default StrategicPanel;
