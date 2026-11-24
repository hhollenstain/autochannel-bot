import Instructions from '../components/Instructions';
import { useTitle } from '../hooks';

export default function InstructionsPage() {
  useTitle('Instructions to use Auto-chan');
  return <Instructions />;
}
