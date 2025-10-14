import { Typography, Box } from '@mui/material';
import { VerifiedUser, RecordVoiceOver, VolumeUp, Translate, Groups } from '@mui/icons-material';
import { PieChart } from '@mui/x-charts/PieChart';
import type { TranscriptionMetadata } from '../../lib/statisticsApi';

interface TranscriptionMetadataChartProps {
  data: TranscriptionMetadata;
}

export function TranscriptionMetadataChart({ data }: TranscriptionMetadataChartProps) {
  // Audio Suitability data
  const suitabilityData = [
    { id: 0, value: data.audio_suitability.suitable, color: '#66bb6a' },
    { id: 1, value: data.audio_suitability.unsuitable, color: '#ef5350' },
    { id: 2, value: data.audio_suitability.unknown, color: '#90a4ae' },
  ].filter(item => item.value > 0);

  const suitabilityLabels = ['Suitable', 'Unsuitable', 'Unknown'];

  // Speaker Gender data
  const genderData = data.speaker_gender.map((item, index) => ({
    id: index,
    value: item.count,
    color: index === 0 ? '#64b5f6' : index === 1 ? '#ba68c8' : '#ffb74d',
  }));

  const genderLabels = data.speaker_gender.map(item => 
    item.gender.charAt(0).toUpperCase() + item.gender.slice(1)
  );

  // Noise data
  const noiseData = [
    { id: 0, value: data.noise.without_noise, color: '#66bb6a' },
    { id: 1, value: data.noise.with_noise, color: '#ef5350' },
    { id: 2, value: data.noise.unknown, color: '#90a4ae' },
  ].filter(item => item.value > 0);

  const noiseLabels = ['Clean', 'With Noise', 'Unknown'];

  // Code Mixing data
  const codeMixingData = [
    { id: 0, value: data.code_mixing.not_mixed, color: '#66bb6a' },
    { id: 1, value: data.code_mixing.code_mixed, color: '#ffb74d' },
    { id: 2, value: data.code_mixing.unknown, color: '#90a4ae' },
  ].filter(item => item.value > 0);

  const codeMixingLabels = ['Pure', 'Code-Mixed', 'Unknown'];

  // Speaker Overlapping data
  const overlappingData = [
    { id: 0, value: data.speaker_overlapping.without_overlap, color: '#66bb6a' },
    { id: 1, value: data.speaker_overlapping.with_overlap, color: '#ef5350' },
    { id: 2, value: data.speaker_overlapping.unknown, color: '#90a4ae' },
  ].filter(item => item.value > 0);

  const overlappingLabels = ['Single Speaker', 'Overlapping', 'Unknown'];

  const chartConfig = {
    width: 200,
    height: 180,
    margin: { top: 10, bottom: 10, left: 10, right: 10 },
  };

  return (
    <Box
      sx={{
        background: 'linear-gradient(135deg, #1a1a2e 0%, #16213e 100%)',
        color: 'white',
        borderRadius: 1,
        boxShadow: 2,
      }}
    >
      <Box sx={{ p: 2 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 0.5 }}>
          <VerifiedUser sx={{ mr: 1, color: '#64b5f6', fontSize: 22 }} />
          <Typography variant="h6" fontWeight="bold" color="white">
            Transcription Quality Metrics
          </Typography>
        </Box>
        <Typography variant="body2" sx={{ mb: 2, color: '#b0bec5' }}>
          Quality indicators and metadata for {data.total_transcriptions.toLocaleString()} transcriptions
        </Typography>

        {/* Grid of charts */}
        <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', sm: 'repeat(3, 1fr)', md: 'repeat(5, 1fr)' }, gap: 2 }}>
          {/* Audio Suitability */}
          <Box
            sx={{
              p: 1.5,
              borderRadius: 2,
              background: 'linear-gradient(135deg, rgba(100, 181, 246, 0.1) 0%, rgba(63, 81, 181, 0.1) 100%)',
              border: '1px solid rgba(100, 181, 246, 0.2)',
            }}
          >
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
              <VerifiedUser sx={{ color: '#64b5f6', mr: 0.5, fontSize: 18 }} />
              <Typography variant="body2" fontWeight="bold" sx={{ color: '#90caf9' }}>
                Audio Suitability
              </Typography>
            </Box>
            <Box sx={{ display: 'flex', justifyContent: 'center' }}>
              <PieChart
                series={[
                  {
                    data: suitabilityData,
                    innerRadius: 35,
                    outerRadius: 70,
                    paddingAngle: 2,
                    cornerRadius: 4,
                  },
                ]}
                {...chartConfig}
              />
            </Box>
            <Box sx={{ mt: 1 }}>
              {suitabilityData.map((item) => (
                <Box key={item.id} sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
                  <Box sx={{ display: 'flex', alignItems: 'center' }}>
                    <Box sx={{ width: 12, height: 12, bgcolor: item.color, borderRadius: 1, mr: 0.5 }} />
                    <Typography variant="caption" sx={{ color: '#b0bec5' }}>{suitabilityLabels[item.id]}</Typography>
                  </Box>
                  <Typography variant="caption" fontWeight="bold" color="white">{item.value.toLocaleString()}</Typography>
                </Box>
              ))}
            </Box>
          </Box>

          {/* Speaker Gender */}
          <Box
            sx={{
              p: 1.5,
              borderRadius: 2,
              background: 'linear-gradient(135deg, rgba(186, 104, 200, 0.1) 0%, rgba(156, 39, 176, 0.1) 100%)',
              border: '1px solid rgba(186, 104, 200, 0.2)',
            }}
          >
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
              <RecordVoiceOver sx={{ color: '#ba68c8', mr: 0.5, fontSize: 18 }} />
              <Typography variant="body2" fontWeight="bold" sx={{ color: '#ce93d8' }}>
                Speaker Gender
              </Typography>
            </Box>
            <Box sx={{ display: 'flex', justifyContent: 'center' }}>
              <PieChart
                series={[
                  {
                    data: genderData,
                    innerRadius: 35,
                    outerRadius: 70,
                    paddingAngle: 2,
                    cornerRadius: 4,
                  },
                ]}
                {...chartConfig}
              />
            </Box>
            <Box sx={{ mt: 1 }}>
              {genderData.map((item, index) => (
                <Box key={item.id} sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
                  <Box sx={{ display: 'flex', alignItems: 'center' }}>
                    <Box sx={{ width: 12, height: 12, bgcolor: item.color, borderRadius: 1, mr: 0.5 }} />
                    <Typography variant="caption" sx={{ color: '#b0bec5' }}>{genderLabels[index]}</Typography>
                  </Box>
                  <Typography variant="caption" fontWeight="bold" color="white">{item.value.toLocaleString()}</Typography>
                </Box>
              ))}
            </Box>
          </Box>

          {/* Noise */}
          <Box
            sx={{
              p: 1.5,
              borderRadius: 2,
              background: 'linear-gradient(135deg, rgba(102, 187, 106, 0.1) 0%, rgba(76, 175, 80, 0.1) 100%)',
              border: '1px solid rgba(102, 187, 106, 0.2)',
            }}
          >
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
              <VolumeUp sx={{ color: '#81c784', mr: 0.5, fontSize: 18 }} />
              <Typography variant="body2" fontWeight="bold" sx={{ color: '#a5d6a7' }}>
                Noise Level
              </Typography>
            </Box>
            <Box sx={{ display: 'flex', justifyContent: 'center' }}>
              <PieChart
                series={[
                  {
                    data: noiseData,
                    innerRadius: 35,
                    outerRadius: 70,
                    paddingAngle: 2,
                    cornerRadius: 4,
                  },
                ]}
                {...chartConfig}
              />
            </Box>
            <Box sx={{ mt: 1 }}>
              {noiseData.map((item) => (
                <Box key={item.id} sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
                  <Box sx={{ display: 'flex', alignItems: 'center' }}>
                    <Box sx={{ width: 12, height: 12, bgcolor: item.color, borderRadius: 1, mr: 0.5 }} />
                    <Typography variant="caption" sx={{ color: '#b0bec5' }}>{noiseLabels[item.id]}</Typography>
                  </Box>
                  <Typography variant="caption" fontWeight="bold" color="white">{item.value.toLocaleString()}</Typography>
                </Box>
              ))}
            </Box>
          </Box>

          {/* Code Mixing */}
          <Box
            sx={{
              p: 1.5,
              borderRadius: 2,
              background: 'linear-gradient(135deg, rgba(255, 183, 77, 0.1) 0%, rgba(255, 152, 0, 0.1) 100%)',
              border: '1px solid rgba(255, 183, 77, 0.2)',
            }}
          >
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
              <Translate sx={{ color: '#ffb74d', mr: 0.5, fontSize: 18 }} />
              <Typography variant="body2" fontWeight="bold" sx={{ color: '#ffcc80' }}>
                Code Mixing
              </Typography>
            </Box>
            <Box sx={{ display: 'flex', justifyContent: 'center' }}>
              <PieChart
                series={[
                  {
                    data: codeMixingData,
                    innerRadius: 35,
                    outerRadius: 70,
                    paddingAngle: 2,
                    cornerRadius: 4,
                  },
                ]}
                {...chartConfig}
              />
            </Box>
            <Box sx={{ mt: 1 }}>
              {codeMixingData.map((item) => (
                <Box key={item.id} sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
                  <Box sx={{ display: 'flex', alignItems: 'center' }}>
                    <Box sx={{ width: 12, height: 12, bgcolor: item.color, borderRadius: 1, mr: 0.5 }} />
                    <Typography variant="caption" sx={{ color: '#b0bec5' }}>{codeMixingLabels[item.id]}</Typography>
                  </Box>
                  <Typography variant="caption" fontWeight="bold" color="white">{item.value.toLocaleString()}</Typography>
                </Box>
              ))}
            </Box>
          </Box>

          {/* Speaker Overlapping */}
          <Box
            sx={{
              p: 1.5,
              borderRadius: 2,
              background: 'linear-gradient(135deg, rgba(239, 83, 80, 0.1) 0%, rgba(244, 67, 54, 0.1) 100%)',
              border: '1px solid rgba(239, 83, 80, 0.2)',
            }}
          >
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
              <Groups sx={{ color: '#ef5350', mr: 0.5, fontSize: 18 }} />
              <Typography variant="body2" fontWeight="bold" sx={{ color: '#ef9a9a' }}>
                Speaker Overlap
              </Typography>
            </Box>
            <Box sx={{ display: 'flex', justifyContent: 'center' }}>
              <PieChart
                series={[
                  {
                    data: overlappingData,
                    innerRadius: 35,
                    outerRadius: 70,
                    paddingAngle: 2,
                    cornerRadius: 4,
                  },
                ]}
                {...chartConfig}
              />
            </Box>
            <Box sx={{ mt: 1 }}>
              {overlappingData.map((item) => (
                <Box key={item.id} sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
                  <Box sx={{ display: 'flex', alignItems: 'center' }}>
                    <Box sx={{ width: 12, height: 12, bgcolor: item.color, borderRadius: 1, mr: 0.5 }} />
                    <Typography variant="caption" sx={{ color: '#b0bec5' }}>{overlappingLabels[item.id]}</Typography>
                  </Box>
                  <Typography variant="caption" fontWeight="bold" color="white">{item.value.toLocaleString()}</Typography>
                </Box>
              ))}
            </Box>
          </Box>
        </Box>
      </Box>
    </Box>
  );
}
