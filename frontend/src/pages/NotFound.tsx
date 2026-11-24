import { Link } from 'react-router';
import { useTitle } from '../hooks';

export default function NotFound() {
  useTitle('Not Found');
  return (
    <>
      <h1>Not Found</h1>
      <p>
        <Link to="/">Back</Link>
      </p>
    </>
  );
}
