import { Link } from 'react-router';
import PageHeader from '../components/PageHeader';
import { useTitle } from '../hooks';

export default function NotFound() {
  useTitle('Not Found');
  return (
    <>
      <PageHeader title="Not Found" description="We couldn't find the page you were looking for." />
      <Link to="/" className="btn btn-primary">
        Back to home
      </Link>
    </>
  );
}
