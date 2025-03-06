import React from 'react';
import { Box, Heading, Text } from '@chakra-ui/react';
import { useParams } from 'react-router-dom';

const Inbox: React.FC = () => {
  const params = useParams();
  const category = params.category;
  const status = params.status;
  const storage = params.storage;
  
  let title = 'All Emails';
  
  if (category) {
    title = `${category.charAt(0).toUpperCase() + category.slice(1)} Emails`;
  } else if (status) {
    title = `${status.charAt(0).toUpperCase() + status.slice(1)} Emails`;
  } else if (storage) {
    title = storage.charAt(0).toUpperCase() + storage.slice(1);
  }
  
  return (
    <Box>
      <Heading as="h1" size="xl" mb={6}>
        {title}
      </Heading>
      <Text>Email list will be displayed here</Text>
    </Box>
  );
};

export default Inbox; 