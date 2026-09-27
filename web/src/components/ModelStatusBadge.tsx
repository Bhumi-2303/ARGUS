import React from 'react';
import { ProvenanceBadge, ProtocolStatus } from './ProvenanceBadge';

export const ModelStatusBadge: React.FC<{ status: string }> = ({ status }) => {
  let mappedStatus: ProtocolStatus = 'final';
  
  if (status === 'verified') mappedStatus = 'final';
  else if (status === 'partial') mappedStatus = 'requires verification';
  else if (status === 'planned') mappedStatus = 'planned';
  else if (status === 'diagnostic') mappedStatus = 'diagnostic-only';

  return <ProvenanceBadge protocolStatus={mappedStatus} compact />;
};
