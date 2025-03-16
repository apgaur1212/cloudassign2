import React, { useEffect, useState } from "react";
import axios from "axios";
import styled from "styled-components";

// Styled Components
const Container = styled.div`
  max-width: 900px;
  margin: auto;
  text-align: center;
  font-family: Arial, sans-serif;
`;

const Form = styled.form`
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-bottom: 20px;
`;

const Input = styled.input`
  padding: 10px;
  font-size: 16px;
  border: 1px solid #ddd;
  border-radius: 5px;
`;

const Button = styled.button`
  padding: 10px;
  font-size: 16px;
  border: none;
  border-radius: 5px;
  background: #28a745;
  color: white;
  cursor: pointer;
  &:hover {
    background: #218838;
  }
`;

const Grid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
`;

const Card = styled.div`
  padding: 20px;
  border-radius: 10px;
  background: #f4f4f4;
  text-align: center;
  box-shadow: 2px 2px 10px rgba(0, 0, 0, 0.1);
`;

const ProductImage = styled.img`
  max-width: 100%;
  height: 150px;
  object-fit: cover;
  border-radius: 10px;
`;

function App() {
  const [products, setProducts] = useState([]);
  const [formData, setFormData] = useState({
    name: "",
    description: "",
    price: "",
    category: "",
    image: null,
  });
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState("");

  // Fetch Products
  useEffect(() => {
    fetchProducts();
  }, []);

  const fetchProducts = async () => {
    setLoading(true);
    try {
      const response = await axios.get("http://127.0.0.1:5000/products");
      setProducts(response.data);
    } catch (error) {
      alert("Error fetching products: " + error.message);
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData({ ...formData, [name]: value });
  };

  const handleFileChange = (e) => {
    setFormData({ ...formData, image: e.target.files[0] });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    const formDataObj = new FormData();
    for (let key in formData) {
      formDataObj.append(key, formData[key]);
    }

    try {
      await axios.post("http://127.0.0.1:5000/add_product", formDataObj);
      alert("Product added successfully!");
      setFormData({ name: "", description: "", price: "", category: "", image: null });
      fetchProducts(); // Refresh products list immediately
    } catch (error) {
      alert("Error adding product: " + error.message);
    }
  };

  const handleSearch = async () => {
    if (!searchQuery.trim()) {
      fetchProducts();
      return;
    }

    setLoading(true);
    try {
      const response = await axios.get(`http://127.0.0.1:5000/search?q=${searchQuery}`);
      setProducts(response.data);
    } catch (error) {
      alert("Error searching products: " + error.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Container>
      <h1>Product Catalog</h1>

      {/* Add Product Form */}
      <Form onSubmit={handleSubmit}>
        <Input type="text" name="name" placeholder="Product Name" onChange={handleChange} value={formData.name} required />
        <Input type="text" name="description" placeholder="Description" onChange={handleChange} value={formData.description} required />
        <Input type="number" name="price" placeholder="Price" onChange={handleChange} value={formData.price} required />
        <Input type="text" name="category" placeholder="Category" onChange={handleChange} value={formData.category} required />
        <Input type="file" name="image" onChange={handleFileChange} />
        <Button type="submit">Add Product</Button>
      </Form>

      {/* Search Bar */}
      <Input
        type="text"
        placeholder="Search by name or category"
        value={searchQuery}
        onChange={(e) => setSearchQuery(e.target.value)}
      />
      <Button onClick={handleSearch}>Search</Button>

      <h2>Available Products</h2>

      {/* Display Products */}
      {loading ? (
        <p>Loading products...</p>
      ) : (
        <Grid>
          {products.length > 0 ? (
            products.map((product) => (
              <Card key={product.id}>
                {product.image_url && <ProductImage src={product.image_url} alt={product.name} />}
                <h3>{product.name}</h3>
                <p>{product.description}</p>
                <p><strong>Price:</strong> ${product.price}</p>
                <p><strong>Category:</strong> {product.category}</p>
              </Card>
            ))
          ) : (
            <p>No products available.</p>
          )}
        </Grid>
      )}
    </Container>
  );
}

export default App;
