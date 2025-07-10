import React, { useState, useEffect } from 'react';
import styled, { keyframes, css } from 'styled-components';
import { motion, AnimatePresence } from 'framer-motion';
import axios from 'axios';
import JSONPretty from 'react-json-pretty';
import 'react-json-pretty/themes/monikai.css';

const glow = keyframes`
  0% { box-shadow: 0 0 5px #00ff00, 0 0 10px #00ff00; }
  50% { box-shadow: 0 0 10px #00ff00, 0 0 20px #00ff00; }
  100% { box-shadow: 0 0 5px #00ff00, 0 0 10px #00ff00; }
`;

const scanline = keyframes`
  0% { transform: translateY(0); }
  100% { transform: translateY(100%); }
`;

const Container = styled.div`
  height: 100%;
  background: rgba(0, 0, 0, 0.95);
  color: #00ff00;
  font-family: 'Fira Code', monospace;
  padding: 2rem;
  position: relative;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  
  &::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 2px;
    background: linear-gradient(to bottom, transparent, #00ff00, transparent);
    animation: ${scanline} 8s linear infinite;
    opacity: 0.1;
  }
`;

const TabBar = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  border-bottom: 1px solid #00ff00;
  padding-bottom: 1rem;
`;

const TabGroup = styled.div`
  display: flex;
  gap: 1rem;
`;

const Tab = styled.button`
  background: transparent;
  border: 1px solid #00ff00;
  color: #00ff00;
  padding: 0.5rem 1.5rem;
  font-family: 'Fira Code', monospace;
  cursor: pointer;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
  
  ${props => props.active && css`
    background: rgba(0, 255, 0, 0.1);
    animation: ${glow} 2s ease-in-out infinite;
    text-shadow: 0 0 10px #00ff00;
  `}
  
  &:hover {
    background: rgba(0, 255, 0, 0.1);
    transform: translateY(-2px);
    box-shadow: 0 5px 15px rgba(0, 255, 0, 0.3);
  }
  
  &:active {
    transform: translateY(0);
  }
`;

const TabIndicator = styled.span`
  display: inline-block;
  margin-left: 0.5rem;
  padding: 0.125rem 0.375rem;
  background: rgba(0, 255, 0, 0.2);
  border: 1px solid #00ff00;
  border-radius: 10px;
  font-size: 0.75rem;
  font-weight: 600;
  min-width: 20px;
  text-align: center;
  animation: ${glow} 3s ease-in-out infinite;
`;

const TabContent = styled(motion.div)`
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
`;

const Section = styled.div`
  margin-bottom: 2rem;
`;

const SectionTitle = styled.h3`
  color: #00ff00;
  text-shadow: 0 0 10px #00ff00;
  margin-bottom: 1rem;
  font-size: 1.2rem;
  text-transform: uppercase;
  letter-spacing: 2px;
`;

const FormGroup = styled.div`
  margin-bottom: 1.5rem;
`;

const Label = styled.label`
  display: block;
  color: #00ff00;
  margin-bottom: 0.5rem;
  font-size: 0.9rem;
  text-transform: uppercase;
  letter-spacing: 1px;
`;

const Input = styled.input`
  width: 100%;
  background: rgba(0, 0, 0, 0.7);
  border: 1px solid #00ff00;
  color: #00ff00;
  padding: 0.75rem;
  font-family: 'Fira Code', monospace;
  font-size: 14px;
  transition: all 0.3s ease;
  
  &:focus {
    outline: none;
    box-shadow: 0 0 10px #00ff00, inset 0 0 5px rgba(0, 255, 0, 0.2);
    background: rgba(0, 0, 0, 0.9);
  }
  
  &::placeholder {
    color: #006600;
  }
`;

const Select = styled.select`
  width: 100%;
  background: rgba(0, 0, 0, 0.7);
  border: 1px solid #00ff00;
  color: #00ff00;
  padding: 0.75rem;
  font-family: 'Fira Code', monospace;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.3s ease;
  
  &:focus {
    outline: none;
    box-shadow: 0 0 10px #00ff00;
  }
  
  option {
    background: #000000;
    color: #00ff00;
  }
`;

const RadioGroup = styled.div`
  display: flex;
  gap: 2rem;
  margin-top: 0.5rem;
`;

const RadioLabel = styled.label`
  display: flex;
  align-items: center;
  cursor: pointer;
  transition: all 0.3s ease;
  
  &:hover {
    text-shadow: 0 0 5px #00ff00;
  }
`;

const RadioInput = styled.input`
  appearance: none;
  width: 20px;
  height: 20px;
  border: 2px solid #00ff00;
  border-radius: 50%;
  margin-right: 0.5rem;
  position: relative;
  cursor: pointer;
  transition: all 0.3s ease;
  
  &:checked {
    background: #00ff00;
    box-shadow: 0 0 10px #00ff00;
    
    &::after {
      content: '';
      position: absolute;
      top: 50%;
      left: 50%;
      transform: translate(-50%, -50%);
      width: 8px;
      height: 8px;
      background: #000000;
      border-radius: 50%;
    }
  }
`;

const Button = styled(motion.button)`
  background: transparent;
  border: 2px solid #00ff00;
  color: #00ff00;
  padding: 0.75rem 2rem;
  font-family: 'Fira Code', monospace;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  text-transform: uppercase;
  letter-spacing: 2px;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
  
  &:hover {
    background: rgba(0, 255, 0, 0.1);
    box-shadow: 0 0 20px #00ff00, inset 0 0 20px rgba(0, 255, 0, 0.1);
    transform: translateY(-2px);
    text-shadow: 0 0 10px #00ff00;
  }
  
  &:active {
    transform: translateY(0);
  }
  
  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
`;

const ResultContainer = styled.div`
  background: rgba(0, 0, 0, 0.7);
  border: 1px solid #00ff00;
  padding: 1.5rem;
  margin-top: 2rem;
  margin-bottom: 2rem;
  overflow-y: auto;
  position: relative;
  flex: 1;
  display: flex;
  flex-direction: column;
  height: calc(100vh - 350px);
  
  &::-webkit-scrollbar {
    width: 8px;
  }
  
  &::-webkit-scrollbar-track {
    background: rgba(0, 255, 0, 0.1);
  }
  
  &::-webkit-scrollbar-thumb {
    background: #00ff00;
    border-radius: 4px;
  }
`;

const ToolCard = styled(motion.div)`
  background: rgba(0, 0, 0, 0.7);
  border: 1px solid #00ff00;
  padding: 1.5rem;
  margin-bottom: 1rem;
  cursor: pointer;
  transition: all 0.3s ease;
  
  &:hover {
    background: rgba(0, 255, 0, 0.05);
    box-shadow: 0 0 15px rgba(0, 255, 0, 0.5);
    transform: translateX(5px);
  }
  
  h4 {
    color: #00ff00;
    margin-bottom: 0.5rem;
    text-shadow: 0 0 5px #00ff00;
  }
  
  p {
    color: #00cc00;
    font-size: 0.9rem;
  }
`;

const ParameterForm = styled.div`
  background: rgba(0, 0, 0, 0.5);
  border: 1px solid #00ff00;
  padding: 1rem;
  margin-top: 1rem;
`;

const LoadingSpinner = styled(motion.div)`
  display: inline-block;
  width: 20px;
  height: 20px;
  border: 2px solid transparent;
  border-top-color: #00ff00;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-left: 1rem;
  
  @keyframes spin {
    to { transform: rotate(360deg); }
  }
`;

const ErrorMessage = styled.div`
  color: #ff0040;
  background: rgba(255, 0, 64, 0.1);
  border: 1px solid #ff0040;
  padding: 1rem;
  margin: 1rem 0;
  text-shadow: 0 0 5px #ff0040;
`;

const SuccessMessage = styled.div`
  color: #00ff00;
  background: rgba(0, 255, 0, 0.1);
  border: 1px solid #00ff00;
  padding: 1rem;
  margin: 1rem 0;
  text-shadow: 0 0 5px #00ff00;
`;

const SavedEndpointsList = styled.div`
  background: rgba(0, 0, 0, 0.7);
  border: 1px solid #00ff00;
  padding: 1rem;
  margin-bottom: 2rem;
  max-height: 300px;
  overflow-y: auto;
  
  &::-webkit-scrollbar {
    width: 8px;
  }
  
  &::-webkit-scrollbar-track {
    background: rgba(0, 255, 0, 0.1);
  }
  
  &::-webkit-scrollbar-thumb {
    background: #00ff00;
    border-radius: 4px;
  }
`;

const SavedEndpointItem = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem;
  margin-bottom: 0.5rem;
  background: rgba(0, 0, 0, 0.5);
  border: 1px solid #006600;
  transition: all 0.3s ease;
  
  &:hover {
    border-color: #00ff00;
    box-shadow: 0 0 10px rgba(0, 255, 0, 0.3);
  }
  
  .info {
    flex: 1;
    margin-right: 1rem;
    
    .name {
      color: #00ff00;
      font-weight: 600;
      margin-bottom: 0.25rem;
    }
    
    .details {
      color: #00cc00;
      font-size: 0.85rem;
      
      .type {
        display: inline-block;
        padding: 0.125rem 0.5rem;
        background: rgba(0, 255, 0, 0.2);
        border: 1px solid #00ff00;
        border-radius: 3px;
        margin-right: 0.5rem;
        text-transform: uppercase;
        font-size: 0.75rem;
      }
    }
  }
  
  .actions {
    display: flex;
    gap: 0.5rem;
  }
`;

const IconButton = styled.button`
  background: transparent;
  border: 1px solid #00ff00;
  color: #00ff00;
  padding: 0.5rem;
  cursor: pointer;
  font-family: 'Fira Code', monospace;
  font-size: 12px;
  transition: all 0.3s ease;
  
  &:hover {
    background: rgba(0, 255, 0, 0.1);
    box-shadow: 0 0 10px rgba(0, 255, 0, 0.5);
  }
  
  &.delete {
    border-color: #ff0040;
    color: #ff0040;
    
    &:hover {
      background: rgba(255, 0, 64, 0.1);
      box-shadow: 0 0 10px rgba(255, 0, 64, 0.5);
    }
  }
`;

const ToggleButton = styled(Button)`
  margin-bottom: 1rem;
  font-size: 14px;
  padding: 0.5rem 1.5rem;
`;

const SavedEndpointsDropdown = styled.div`
  position: relative;
`;

const SavedEndpointsButton = styled.button`
  background: transparent;
  border: 1px solid #00ff00;
  color: #00ff00;
  padding: 0.5rem 1rem;
  font-family: 'Fira Code', monospace;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  
  &:hover {
    background: rgba(0, 255, 0, 0.1);
    box-shadow: 0 0 10px rgba(0, 255, 0, 0.5);
  }
  
  .count {
    background: rgba(0, 255, 0, 0.2);
    padding: 0.125rem 0.375rem;
    border-radius: 10px;
    font-size: 0.75rem;
  }
`;

const SavedEndpointsMenu = styled(motion.div)`
  position: absolute;
  top: 100%;
  right: 0;
  margin-top: 0.5rem;
  background: rgba(0, 0, 0, 0.95);
  border: 1px solid #00ff00;
  box-shadow: 0 5px 20px rgba(0, 255, 0, 0.3);
  min-width: 350px;
  max-width: 500px;
  z-index: 100;
`;

const MCPInterface = () => {
  const [activeTab, setActiveTab] = useState('connect');
  const [endpoint, setEndpoint] = useState('');
  const [transportType, setTransportType] = useState('http');
  const [apiKey, setApiKey] = useState('');
  const [authHeader, setAuthHeader] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [discoveryResult, setDiscoveryResult] = useState(null);
  const [selectedTool, setSelectedTool] = useState(null);
  const [toolParameters, setToolParameters] = useState({});
  const [resources, setResources] = useState([]);
  const [prompts, setPrompts] = useState([]);
  const [savedEndpoints, setSavedEndpoints] = useState([]);
  const [showSavedEndpoints, setShowSavedEndpoints] = useState(false);
  const [connectionSettingsCollapsed, setConnectionSettingsCollapsed] = useState(false);

  // Load saved endpoints from localStorage on mount
  useEffect(() => {
    const loadSavedEndpoints = () => {
      try {
        const saved = localStorage.getItem('mcpeek_saved_endpoints');
        if (saved) {
          setSavedEndpoints(JSON.parse(saved));
        }
      } catch (err) {
        console.error('Failed to load saved endpoints:', err);
      }
    };
    loadSavedEndpoints();
  }, []);
  
  // Handle click outside to close dropdown
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (showSavedEndpoints && !event.target.closest('.saved-endpoints-container')) {
        setShowSavedEndpoints(false);
      }
    };
    
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, [showSavedEndpoints]);

  // Save endpoint to localStorage
  const saveEndpoint = (endpointData) => {
    try {
      const newEndpoint = {
        id: Date.now(),
        endpoint: endpointData.endpoint,
        transportType: endpointData.transportType,
        name: endpointData.name || endpointData.endpoint.substring(0, 50),
        apiKey: endpointData.apiKey,
        authHeader: endpointData.authHeader,
        savedAt: new Date().toISOString(),
        capabilities: endpointData.capabilities
      };
      
      const updated = [...savedEndpoints.filter(e => e.endpoint !== endpointData.endpoint), newEndpoint];
      setSavedEndpoints(updated);
      localStorage.setItem('mcpeek_saved_endpoints', JSON.stringify(updated));
    } catch (err) {
      console.error('Failed to save endpoint:', err);
    }
  };

  // Load a saved endpoint
  const loadSavedEndpoint = (saved) => {
    setEndpoint(saved.endpoint);
    setTransportType(saved.transportType);
    setApiKey(saved.apiKey || '');
    setAuthHeader(saved.authHeader || '');
    setShowSavedEndpoints(false);
    setSuccess(`Loaded saved endpoint: ${saved.name}`);
  };

  // Delete a saved endpoint
  const deleteSavedEndpoint = (id) => {
    const updated = savedEndpoints.filter(e => e.id !== id);
    setSavedEndpoints(updated);
    localStorage.setItem('mcpeek_saved_endpoints', JSON.stringify(updated));
  };

  const handleDiscover = async () => {
    if (!endpoint) {
      setError('Please set an endpoint first');
      return;
    }

    setIsLoading(true);
    setError('');
    setSuccess('');

    try {
      const headers = {};
      if (apiKey) headers['X-API-Key'] = apiKey;
      if (authHeader) headers['X-Auth-Header'] = authHeader;

      // Ensure the endpoint is sent as-is without modification
      // The backend will determine if it's HTTP or STDIO based on the format
      const response = await axios.post('/api/discover', {
        endpoint: endpoint.trim(),
        verbosity: 2,
        tool_tickle: true
      }, { headers });

      if (response.data.success) {
        setDiscoveryResult(response.data.data);
        setSuccess('Discovery completed successfully!');
        
        // Extract tools, resources, and prompts
        if (response.data.data.capabilities) {
          setResources(response.data.data.capabilities.resources || []);
          setPrompts(response.data.data.capabilities.prompts || []);
        }
        
        // Save successful endpoint
        saveEndpoint({
          endpoint,
          transportType,
          apiKey,
          authHeader,
          capabilities: response.data.data.capabilities
        });
        
        // Collapse connection settings to make more room
        setConnectionSettingsCollapsed(true);
      } else {
        setError(response.data.error || 'Unknown error occurred');
      }
    } catch (err) {
      if (err.response && err.response.data && err.response.data.error) {
        setError(err.response.data.error);
      } else {
        setError(err.message || 'Network error occurred');
      }
    } finally {
      setIsLoading(false);
    }
  };

  const handleExecuteTool = async (toolName) => {
    setIsLoading(true);
    setError('');
    setSuccess('');

    try {
      const headers = {};
      if (apiKey) headers['X-API-Key'] = apiKey;
      if (authHeader) headers['X-Auth-Header'] = authHeader;

      const response = await axios.post('/api/execute/tool', {
        endpoint: endpoint.trim(),
        tool_name: toolName,
        parameters: toolParameters[toolName] || {}
      }, { headers });

      if (response.data.success) {
        setSuccess(`Tool ${toolName} executed successfully!`);
        // Update results display
      } else {
        setError(response.data.error || 'Tool execution failed');
      }
    } catch (err) {
      if (err.response && err.response.data && err.response.data.error) {
        setError(err.response.data.error);
      } else {
        setError(err.message || 'Network error occurred');
      }
    } finally {
      setIsLoading(false);
    }
  };

  const renderConnectTab = () => (
    <TabContent
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
    >
      <Section>
        <SectionTitle 
          style={{ cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '1rem' }}
          onClick={() => setConnectionSettingsCollapsed(!connectionSettingsCollapsed)}
        >
          Connection Settings
          <span style={{ fontSize: '0.8rem', opacity: 0.7 }}>
            {connectionSettingsCollapsed ? '▶' : '▼'}
          </span>
        </SectionTitle>
        
        <AnimatePresence>
          {!connectionSettingsCollapsed && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              exit={{ opacity: 0, height: 0 }}
              transition={{ duration: 0.3 }}
            >
              <FormGroup>
                <Label>Transport Type</Label>
                <RadioGroup>
            <RadioLabel>
              <RadioInput
                type="radio"
                name="transport"
                value="http"
                checked={transportType === 'http'}
                onChange={(e) => setTransportType(e.target.value)}
              />
              HTTP/HTTPS
            </RadioLabel>
            <RadioLabel>
              <RadioInput
                type="radio"
                name="transport"
                value="stdio"
                checked={transportType === 'stdio'}
                onChange={(e) => setTransportType(e.target.value)}
              />
              STDIO (Local)
            </RadioLabel>
          </RadioGroup>
        </FormGroup>

        <FormGroup>
          <Label>Endpoint {transportType === 'http' ? 'URL' : 'Command'}</Label>
          <Input
            type="text"
            value={endpoint}
            onChange={(e) => setEndpoint(e.target.value)}
            placeholder={transportType === 'http' ? 'https://api.example.com/mcp' : '/path/to/python /path/to/script.py --args'}
          />
          {transportType === 'stdio' && (
            <small style={{ color: '#00cc00', marginTop: '0.5rem', display: 'block' }}>
              Enter the full command to launch the MCP server (e.g., python script.py)
            </small>
          )}
        </FormGroup>

        {transportType === 'http' && (
          <>
            <FormGroup>
              <Label>API Key (Optional)</Label>
              <Input
                type="password"
                value={apiKey}
                onChange={(e) => setApiKey(e.target.value)}
                placeholder="Enter API key if required"
              />
            </FormGroup>

            <FormGroup>
              <Label>Custom Auth Header (Optional)</Label>
              <Input
                type="text"
                value={authHeader}
                onChange={(e) => setAuthHeader(e.target.value)}
                placeholder="Bearer token or custom header"
              />
            </FormGroup>
          </>
        )}

              <Button
                onClick={handleDiscover}
                disabled={isLoading || !endpoint}
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
              >
                {isLoading ? (
                  <>
                    Discovering
                    <LoadingSpinner />
                  </>
                ) : (
                  'Discover Endpoint'
                )}
              </Button>
            </motion.div>
          )}
        </AnimatePresence>
      </Section>

      {error && <ErrorMessage>{error}</ErrorMessage>}
      {success && <SuccessMessage>{success}</SuccessMessage>}

      {discoveryResult && (
        <ResultContainer>
          <SectionTitle>Discovery Results</SectionTitle>
          <div style={{ flex: 1, overflow: 'auto' }}>
            <JSONPretty data={discoveryResult} />
          </div>
        </ResultContainer>
      )}
    </TabContent>
  );

  const renderToolsTab = () => {
    try {
      const tools = discoveryResult?.capabilities?.tools || [];
      
      return (
        <TabContent
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -20 }}
        >
          <Section>
            <SectionTitle>Available Tools</SectionTitle>
            
            {tools.length > 0 ? (
              tools.map((tool) => {
                if (!tool || !tool.name) return null;
                
                return (
                  <ToolCard
                    key={tool.name}
                    onClick={() => setSelectedTool(tool)}
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                  >
                    <h4>{tool.name}</h4>
                    <p>{tool.description || 'No description available'}</p>
                    
                    {selectedTool?.name === tool.name && (
                      <ParameterForm onClick={(e) => e.stopPropagation()}>
                        <h5>Parameters:</h5>
                        {tool.inputSchema?.properties ? (
                          Object.entries(tool.inputSchema.properties).map(([key, schema]) => {
                            if (!key || !schema) return null;
                            
                            return (
                              <FormGroup key={key}>
                                <Label>
                                  {key} {tool.inputSchema?.required?.includes(key) ? '*' : ''}
                                </Label>
                                <Input
                                  type="text"
                                  placeholder={schema.description || `Enter ${key}`}
                                  onChange={(e) => setToolParameters({
                                    ...toolParameters,
                                    [tool.name]: {
                                      ...toolParameters[tool.name],
                                      [key]: e.target.value
                                    }
                                  })}
                                />
                              </FormGroup>
                            );
                          })
                        ) : (
                          <p>No parameters required</p>
                        )}
                        <Button
                          onClick={() => handleExecuteTool(tool.name)}
                          disabled={isLoading}
                          whileHover={{ scale: 1.05 }}
                          whileTap={{ scale: 0.95 }}
                        >
                          Execute Tool
                        </Button>
                      </ParameterForm>
                    )}
                  </ToolCard>
                );
              })
            ) : (
              <p>No tools available. Please discover an endpoint first.</p>
            )}
          </Section>
        </TabContent>
      );
    } catch (error) {
      console.error('Error rendering tools tab:', error);
      return (
        <TabContent>
          <Section>
            <ErrorMessage>Error loading tools. Please try discovering the endpoint again.</ErrorMessage>
          </Section>
        </TabContent>
      );
    }
  };

  const renderResourcesTab = () => {
    try {
      return (
        <TabContent
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -20 }}
        >
          <Section>
            <SectionTitle>Available Resources</SectionTitle>
            {resources.length > 0 ? (
              resources.map((resource, index) => (
                <ToolCard
                  key={resource.uri || `resource-${index}`}
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                >
                  <h4>{resource.name || 'Unnamed Resource'}</h4>
                  <p>URI: {resource.uri || 'No URI'}</p>
                  <p>{resource.description || 'No description available'}</p>
                </ToolCard>
              ))
            ) : (
              <p>No resources available. Please discover an endpoint first.</p>
            )}
          </Section>
        </TabContent>
      );
    } catch (error) {
      console.error('Error rendering resources tab:', error);
      return (
        <TabContent>
          <Section>
            <ErrorMessage>Error loading resources.</ErrorMessage>
          </Section>
        </TabContent>
      );
    }
  };

  const renderPromptsTab = () => {
    try {
      return (
        <TabContent
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -20 }}
        >
          <Section>
            <SectionTitle>Available Prompts</SectionTitle>
            {prompts.length > 0 ? (
              prompts.map((prompt, index) => (
                <ToolCard
                  key={prompt.name || `prompt-${index}`}
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                >
                  <h4>{prompt.name || 'Unnamed Prompt'}</h4>
                  <p>{prompt.description || 'No description available'}</p>
                </ToolCard>
              ))
            ) : (
              <p>No prompts available. Please discover an endpoint first.</p>
            )}
          </Section>
        </TabContent>
      );
    } catch (error) {
      console.error('Error rendering prompts tab:', error);
      return (
        <TabContent>
          <Section>
            <ErrorMessage>Error loading prompts.</ErrorMessage>
          </Section>
        </TabContent>
      );
    }
  };

  return (
    <Container>
      <TabBar>
        <TabGroup>
          <Tab active={activeTab === 'connect'} onClick={() => setActiveTab('connect')}>
            Connect
          </Tab>
          <Tab active={activeTab === 'tools'} onClick={() => setActiveTab('tools')}>
            Tools
            {discoveryResult?.capabilities?.tools?.length > 0 && (
              <TabIndicator>{discoveryResult.capabilities.tools.length}</TabIndicator>
            )}
          </Tab>
          <Tab active={activeTab === 'resources'} onClick={() => setActiveTab('resources')}>
            Resources
            {resources.length > 0 && (
              <TabIndicator>{resources.length}</TabIndicator>
            )}
          </Tab>
          <Tab active={activeTab === 'prompts'} onClick={() => setActiveTab('prompts')}>
            Prompts
            {prompts.length > 0 && (
              <TabIndicator>{prompts.length}</TabIndicator>
            )}
          </Tab>
        </TabGroup>
        
        {savedEndpoints.length > 0 && (
          <SavedEndpointsDropdown className="saved-endpoints-container">
            <SavedEndpointsButton onClick={() => setShowSavedEndpoints(!showSavedEndpoints)}>
              Saved Endpoints
              <span className="count">{savedEndpoints.length}</span>
            </SavedEndpointsButton>
            
            <AnimatePresence>
              {showSavedEndpoints && (
                <SavedEndpointsMenu
                  initial={{ opacity: 0, y: -10 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -10 }}
                  transition={{ duration: 0.2 }}
                >
                  <SavedEndpointsList>
                    {savedEndpoints.map((saved) => (
                      <SavedEndpointItem key={saved.id}>
                        <div className="info">
                          <div className="name">{saved.name}</div>
                          <div className="details">
                            <span className="type">{saved.transportType}</span>
                            <span>Saved {new Date(saved.savedAt).toLocaleDateString()}</span>
                          </div>
                        </div>
                        <div className="actions">
                          <IconButton
                            onClick={() => {
                              loadSavedEndpoint(saved);
                              setShowSavedEndpoints(false);
                            }}
                            title="Load this endpoint"
                          >
                            LOAD
                          </IconButton>
                          <IconButton
                            className="delete"
                            onClick={() => deleteSavedEndpoint(saved.id)}
                            title="Delete this endpoint"
                          >
                            DELETE
                          </IconButton>
                        </div>
                      </SavedEndpointItem>
                    ))}
                  </SavedEndpointsList>
                </SavedEndpointsMenu>
              )}
            </AnimatePresence>
          </SavedEndpointsDropdown>
        )}
      </TabBar>

      <AnimatePresence mode="wait">
        {activeTab === 'connect' && renderConnectTab()}
        {activeTab === 'tools' && renderToolsTab()}
        {activeTab === 'resources' && renderResourcesTab()}
        {activeTab === 'prompts' && renderPromptsTab()}
      </AnimatePresence>
    </Container>
  );
};

export default MCPInterface;