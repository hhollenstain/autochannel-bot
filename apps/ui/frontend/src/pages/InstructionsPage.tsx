import Instructions from '../components/Instructions';
import PageHeader from '../components/PageHeader';
import { useTitle } from '../hooks';

export default function InstructionsPage() {
  useTitle('Instructions to use Auto-chan');
  return (
    <>
      <PageHeader
        title="How to use AutoChannel"
        description="Get Auto-chan running in your server in a few minutes."
      />
      <Instructions />
    </>
  );
}
