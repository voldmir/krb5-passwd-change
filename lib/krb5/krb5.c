#include <Python.h>
#include <krb5.h>

static PyObject *Krb5Error;

#define RETURN_ON_ERROR(message, code)                         \
    do                                                         \
        if (code != 0)                                         \
        {                                                      \
            const char *error;                                 \
            error = krb5_get_error_message(ctx, code);         \
            PyErr_Format(Krb5Error, "%s: %s", message, error); \
            krb5_free_error_message(ctx, error);               \
            return NULL;                                       \
        }                                                      \
    while (0)

static PyObject *
k5_get_init_creds_password(PyObject *self, PyObject *args)
{
    char *name, *password;
    krb5_context ctx;
    krb5_error_code code;
    krb5_ccache ccache;
    krb5_principal principal;
    krb5_get_init_creds_opt options;
    krb5_creds creds;

    if (!PyArg_ParseTuple(args, "ss", &name, &password))
        return NULL;

    /* Initialize parameters. */
    code = krb5_init_context(&ctx);
    RETURN_ON_ERROR("krb5_init_context()", code);
    code = krb5_parse_name(ctx, name, &principal);
    RETURN_ON_ERROR("krb5_parse_name()", code);
    krb5_get_init_creds_opt_init(&options);
    memset(&creds, 0, sizeof(creds));

    /* Get the credentials. */
    code = krb5_get_init_creds_password(ctx, &creds, principal, password,
                                        NULL, NULL, 0, NULL, &options);
    RETURN_ON_ERROR("krb5_get_init_creds_password()", code);

    /* Store the credential in the credential cache. */
    code = krb5_cc_default(ctx, &ccache);
    RETURN_ON_ERROR("krb5_cc_default()", code);
    code = krb5_cc_initialize(ctx, ccache, principal);
    RETURN_ON_ERROR("krb5_cc_initialize()", code);
    code = krb5_cc_store_cred(ctx, ccache, &creds);
    RETURN_ON_ERROR("krb5_cc_store_creds()", code);
    krb5_cc_close(ctx, ccache);

    Py_INCREF(Py_None);
    return Py_None;
}

static void
_k5_set_password_error(krb5_data *result_code_string, krb5_data *result_string)
{
    char *p1, *p2;

    p1 = malloc((result_code_string->length) + 1);
    if (p1 == NULL)
    {
        PyErr_NoMemory();
        return;
    }
    if (result_code_string->data)
    {
        strncpy(p1, result_code_string->data, result_code_string->length);
    }
    p1[result_code_string->length] = '\0';

    p2 = malloc((result_string->length) + 1);
    if (p1 == NULL)
    {
        PyErr_NoMemory();
        return;
    }
    if (result_string->data)
    {
        strncpy(p2, result_string->data, result_string->length);
    }
    p2[result_string->length] = '\0';

    PyErr_Format(Krb5Error, "%s%s%s", p1, (*p1 && *p2) ? ": " : "", p2);

    free(p1);
    free(p2);
}

static PyObject *
k5_set_password(PyObject *self, PyObject *args)
{
    int result_code;
    char *name, *newpass;
    krb5_context ctx;
    krb5_error_code code;
    krb5_principal principal;
    krb5_data result_code_string, result_string;
    krb5_ccache ccache;

    if (!PyArg_ParseTuple(args, "ss", &name, &newpass))
        return NULL;

    /* Initialize parameters. */
    code = krb5_init_context(&ctx);
    RETURN_ON_ERROR("krb5_init_context()", code);
    code = krb5_parse_name(ctx, name, &principal);
    RETURN_ON_ERROR("krb5_parse_name()", code);

    /* Get credentials */
    code = krb5_cc_default(ctx, &ccache);
    RETURN_ON_ERROR("krb5_cc_default()", code);

    /* Set password */
    code = krb5_set_password_using_ccache(ctx, ccache, newpass, principal,
                                          &result_code, &result_code_string,
                                          &result_string);
    RETURN_ON_ERROR("krb5_set_password_using_ccache()", code);

    /* Any other error? */
    if (result_code != 0)
    {
        _k5_set_password_error(&result_code_string, &result_string);
        return NULL;
    }

    /* Free up results. */
    if (result_code_string.data != NULL)
        free(result_code_string.data);
    if (result_string.data != NULL)
        free(result_string.data);

    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject *
k5_change_password(PyObject *self, PyObject *args)
{
    int result_code;
    char *name, *oldpass, *newpass;
    krb5_context ctx;
    krb5_error_code code;
    krb5_principal principal;
    krb5_get_init_creds_opt options;
    krb5_creds creds;
    krb5_data result_code_string, result_string;

    if (!PyArg_ParseTuple(args, "sss", &name, &oldpass, &newpass))
        return NULL;

    /* Initialize parameters. */
    code = krb5_init_context(&ctx);
    RETURN_ON_ERROR("krb5_init_context()", code);
    code = krb5_parse_name(ctx, name, &principal);
    RETURN_ON_ERROR("krb5_parse_name()", code);

    /* Get credentials using the password. */
    krb5_get_init_creds_opt_init(&options);
    krb5_get_init_creds_opt_set_tkt_life(&options, 5 * 60);
    krb5_get_init_creds_opt_set_renew_life(&options, 0);
    krb5_get_init_creds_opt_set_forwardable(&options, 0);
    krb5_get_init_creds_opt_set_proxiable(&options, 0);
    memset(&creds, 0, sizeof(creds));
    code = krb5_get_init_creds_password(ctx, &creds, principal, oldpass,
                                        NULL, NULL, 0, "kadmin/changepw",
                                        &options);
    RETURN_ON_ERROR("krb5_get_init_creds_password()", code);

    code = krb5_change_password(ctx, &creds, newpass, &result_code,
                                &result_code_string, &result_string);
    RETURN_ON_ERROR("krb5_change_password()", code);

    /* Any other error? */
    if (result_code != 0)
    {
        _k5_set_password_error(&result_code_string, &result_string);
        return NULL;
    }

    /* Free up results. */
    if (result_code_string.data != NULL)
        free(result_code_string.data);
    if (result_string.data != NULL)
        free(result_string.data);

    Py_INCREF(Py_None);
    return Py_None;
}

struct module_state
{
    PyObject *error;
};

#define GETSTATE(m) ((struct module_state *)PyModule_GetState(m))

static PyMethodDef k5_methods[] =
    {
        {"get_init_creds_password",
         (PyCFunction)k5_get_init_creds_password, METH_VARARGS},
        {"set_password",
         (PyCFunction)k5_set_password, METH_VARARGS},
        {"change_password",
         (PyCFunction)k5_change_password, METH_VARARGS},
        {NULL, NULL}};

static int k5_traverse(PyObject *m, visitproc visit, void *arg)
{
    Py_VISIT(GETSTATE(m)->error);
    return 0;
}

static int k5_clear(PyObject *m)
{
    Py_CLEAR(GETSTATE(m)->error);
    return 0;
}

static struct PyModuleDef moduledef = {
    PyModuleDef_HEAD_INIT,
    "krb5",
    NULL,
    sizeof(struct module_state),
    k5_methods,
    NULL,
    k5_traverse,
    k5_clear,
    NULL};

#define INITERROR return NULL

PyMODINIT_FUNC
PyInit_krb5(void)
{
    PyObject *module;

    initialize_krb5_error_table();

    module = PyModule_Create(&moduledef);

    if (module == NULL)
        INITERROR;

    Krb5Error = PyErr_NewException("krb5.error", NULL, NULL);
    Py_XINCREF(Krb5Error);
    if (PyModule_AddObject(module, "error", Krb5Error) < 0)
    {
        Py_XDECREF(Krb5Error);
        Py_CLEAR(Krb5Error);
        Py_DECREF(module);
        return NULL;
    }

    return module;
}
